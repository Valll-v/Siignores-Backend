from django.db import models


# Create your models here.
class Course(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, blank=False, null=False)
    name = models.CharField(max_length=100, null=False, blank=False, verbose_name='Название')
    image = models.ImageField(null=False, blank=False, upload_to="media/", verbose_name='Картинка')

    class Meta:
        managed = True
        db_table = 'courses'


class CourseSubscription(models.Model):
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, blank=False, null=False)
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, blank=False, null=False)

    class Meta:
        managed = True
        db_table = 'subs'


def set_module_id(course_id):
    all_modules = sorted(Module.objects.filter(course_id=course_id), key=lambda x: x.id)
    return all_modules[-1].id + 1 if all_modules else 1


def set_lesson_id(course_id):
    all_modules = sorted(Lesson.objects.filter(course_id=course_id), key=lambda x: x.id)
    return all_modules[-1].id + 1 if all_modules else 1


class Module(models.Model):
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, blank=False, null=False)
    in_course_id = models.IntegerField(null=False, blank=False)
    image = models.ImageField(null=False, blank=False, upload_to="media/", verbose_name='Картинка')

    class Meta:
        managed = True
        db_table = 'modules'


class Lesson(models.Model):
    in_course_id = models.IntegerField(null=False, blank=False)
    module = models.ForeignKey('courses.Module', on_delete=models.CASCADE, blank=False, null=False)
    name = models.CharField(max_length=1000, null=False, blank=False, verbose_name='Название')
