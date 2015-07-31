""" Database ORM models managed by this Django app """

from django.contrib.auth.models import Group, User
from django.db import models

from model_utils.models import TimeStampedModel
from student.models import AnonymousUserId


class Project(TimeStampedModel):
    """
    Model representing the Project concept.  Projects are an
    intersection of Courses, CourseContent, and Workgroups.
    """
    course_id = models.CharField(max_length=255)
    content_id = models.CharField(max_length=255)

    class Meta:
        """ Meta class for defining additional model characteristics """
        unique_together = ("course_id", "content_id")


class Workgroup(TimeStampedModel):
    """
    Model representing the Workgroup concept.  Workgroups are an
    intersection of Users and CourseContent, although they can also be
    related to other Groups.
    """
    name = models.CharField(max_length=255, null=True, blank=True)
    project = models.ForeignKey(Project, related_name="workgroups")
    users = models.ManyToManyField(User, related_name="workgroups", blank=True, null=True)
    groups = models.ManyToManyField(Group, related_name="workgroups", blank=True, null=True)


class WorkgroupReview(TimeStampedModel):
    """
    Model representing the Workgroup Review concept.  A Workgroup Review is
    a single question/answer combination for a particular Workgroup in the
    context of a specific Project, as defined in the Group Project XBlock
    schema.  There can be more than one Project Review entry for a given Project.
    """
    workgroup = models.ForeignKey(Workgroup, related_name="workgroup_reviews")
    reviewer = models.CharField(max_length=255)  # AnonymousUserId
    question = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)


class WorkgroupSubmission(TimeStampedModel):
    """
    Model representing the Submission concept.  A Submission is a project artifact
    created by the Users in a Workgroup.  The document fields are defined by the
    'Group Project' XBlock and data for a specific instance is persisted here
    """
    workgroup = models.ForeignKey(Workgroup, related_name="submissions")
    user = models.ForeignKey(User, related_name="submissions")
    document_id = models.CharField(max_length=255)
    document_url = models.CharField(max_length=255)
    document_mime_type = models.CharField(max_length=255)


class WorkgroupSubmissionReview(TimeStampedModel):
    """
    Model representing the Submission Review concept.  A Submission Review is
    essentially a single question/answer combination for a particular Submission,
    defined in the Group Project XBlock schema.  There can be more than one
    Submission Review entry for a given Submission.
    """
    submission = models.ForeignKey(WorkgroupSubmission, related_name="reviews")
    reviewer = models.CharField(max_length=255)  # AnonymousUserId
    question = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)


class WorkgroupPeerReview(TimeStampedModel):
    """
    Model representing the Peer Review concept.  A Peer Review is a record of a
    specific question/answer defined in the Group Project XBlock schema.  There
    can be more than one Peer Review entry for a given User.
    """
    workgroup = models.ForeignKey(Workgroup, related_name="peer_reviews")
    user = models.ForeignKey(User, related_name="workgroup_peer_reviewees")
    reviewer = models.CharField(max_length=255)  # AnonymousUserId
    question = models.CharField(max_length=255)
    answer = models.CharField(max_length=255)
