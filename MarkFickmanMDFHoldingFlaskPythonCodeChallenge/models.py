import sys
from django.utils.timezone import now
try:
    from django.db import models
except Exception:
    print("There was an error loading django modules. Do you have django installed?")
    sys.exit()

from django.conf import settings


# Instructor model
class Instructor(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    full_time = models.BooleanField(default=True)
    total_learners = models.IntegerField()

    def __str__(self):
        return self.user.username


# Learner model
class Learner(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    STUDENT = 'student'
    DEVELOPER = 'developer'
    DATA_SCIENTIST = 'data_scientist'
    DATABASE_ADMIN = 'dba'
    OCCUPATION_CHOICES = [
        (STUDENT, 'Student'),
        (DEVELOPER, 'Developer'),
        (DATA_SCIENTIST, 'Data Scientist'),
        (DATABASE_ADMIN, 'Database Admin')
    ]
    occupation = models.CharField(
        null=False,
        max_length=20,
        choices=OCCUPATION_CHOICES,
        default=STUDENT
    )
    social_link = models.URLField(max_length=200)

    def __str__(self):
        # JCA Updated to be f-string.
        return f'{self.user.username}, {self.occupation}'


# Course model
class Course(models.Model):
    name = models.CharField(null=False, max_length=30, default='online course')
    image = models.ImageField(upload_to='course_images/')
    description = models.CharField(max_length=1000)
    pub_date = models.DateField(null=True)
    instructors = models.ManyToManyField(Instructor)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Enrollment')
    total_enrollment = models.IntegerField(default=0)
    is_enrolled = False

    def __str__(self):
        # JCA Updated to be f-string.
        return f'Name: {self.name}, Description: {self.description}'


# Lesson model
class Lesson(models.Model):
    title = models.CharField(max_length=200, default="title")
    order = models.IntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.TextField()


# Enrollment model
# <HINT> Once a user enrolled a class, an enrollment entry should be created between the user and course
# And we could use the enrollment to track information such as exam submissions
class Enrollment(models.Model):
    AUDIT = 'audit'
    HONOR = 'honor'
    BETA = 'BETA'
    COURSE_MODES = [
        (AUDIT, 'Audit'),
        (HONOR, 'Honor'),
        (BETA, 'BETA')
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateField(default=now)
    mode = models.CharField(max_length=5, choices=COURSE_MODES, default=AUDIT)
    rating = models.FloatField(default=5.0)


# 03/2023 JCA: New models included ------------
class Question(models.Model):
    """Model to track the questions in an exam for each course.
    Note: 1 Question has multiple * Choice.
    """
    question_text = models.CharField(max_length=300)
    question_value = models.IntegerField(default=1)  # 1 point per question default
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)

    def get_question_score(self, choices_selected: list = None) -> bool:
        """This method will calculate the total score for the question based on user answers.
        Full mark is only possible when all selections are correct. [No wrong answers]
        :param choices_selected: list: Choices made by users.
        :return bool: Correct (True), any wrong (False).
        """
        # Get correct answers for this question using backward relationship.
        return True if self.choice_set.filter(is_correct=True).count() ==\
                       self.choice_set.filter(is_correct=True, id__in=choices_selected).count() else False

    def __str__(self):
        """Default string when calling object"""
        return f'{self.question_text} ({self.question_value} {"point" if self.question_value == 1 else "points"})'


class Choice(models.Model):
    """Store choices for questions."""
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE)

    def __str__(self):
        """Default string when calling object"""
        return self.choice_text


class Submission(models.Model):
    """Store the submissions done by a user."""
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    choices = models.ManyToManyField(Choice)
