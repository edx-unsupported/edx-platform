import csv
import logging

from rest_framework.authentication import SessionAuthentication
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from edx_rest_framework_extensions.auth.session.authentication import SessionAuthenticationAllowInactiveUser
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .tasks import migrate_progress, OUTCOME_MIGRATED

log = logging.getLogger(__name__)


class MigrateProgressView(APIView):
    """
    Migrates user progress for a set of user pairs.
    Only admins can use this.
    """

    authentication_classes = (
        JwtAuthentication,
        SessionAuthentication,
        SessionAuthenticationAllowInactiveUser,
    )

    permission_classes = (
        permissions.IsAuthenticated,
        permissions.IsAdminUser,
    )

    def post(self, request):
        """
        POST /api/user/v1/completion/migrate/

        Migrate user progress.
        """
        csv_file = request.FILES['file']
        recepient_address = request.POST.get('recepient_address')

        reader = csv.DictReader(csv_file)

        if not {'course', 'source_email', 'dest_email'}.issubset(set(reader.fieldnames)):
            log.warning('Received invalid csv.')
            return Response(status=411)

        # Extract list to be used in migration task
        migrate_list = [
            (row['course'], row['source_email'], row['dest_email']) for row in reader
            if row.get('outcome') != OUTCOME_MIGRATED  # Ignore lines marked as migrated
        ]

        # Start background task to migrate progress for given users
        migrate_progress.delay(
            migrate_list,
            [recepient_address] if recepient_address else None
        )

        log.info('Scheduled user progress migration. Items to process: %s', len(migrate_list))

        return Response(status=200)
