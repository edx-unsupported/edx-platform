import csv

from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from edx_rest_framework_extensions.auth.session.authentication import SessionAuthenticationAllowInactiveUser
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .tasks import merge_completions


class MergeCompletion(APIView):
    """
    Merges completions for a set of user pairs.
    Only admins can use this.
    """
    authentication_classes = (JwtAuthentication, )
    permission_classes = (permissions.IsAuthenticated, SessionAuthenticationAllowInactiveUser)

    def post(self, request):
        """
        POST /api/user/v1/completion/merge/

        Merge completions.
        """
        # Get file from request
        f = request.FILES['file']

        # Parse CSV content to create a list
        reader = csv.DictReader(f)
        if not set(['course', 'source_email', 'dest_email']) < set(reader.fieldnames):
            # Assert correct csv is uploaded
            return Response(status=400)
        # Extract list to be used in migration task
        merge_list = [
            (row['course'], row['source_email'], row['dest_email']) for row in reader
            if row.get('outcome') != 'migrated'  # Ignore lines marked as migrated
        ]
        # Start background task to merge progress for given users
        merge_completions.delay(merge_list)
        return Response(status=200)
