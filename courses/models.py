from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Course(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, blank=False, null=False)
    name = models.CharField(max_length=100, null=False, blank=False, verbose_name='Название')
    image = models.ImageField(null=True, blank=True, upload_to="media/", verbose_name='Картинка')
    description = models.CharField(max_length=2000, null=False, blank=False, verbose_name='Название',
                                   default="Базовое описание (базированное)")

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


def set_lesson_id(module_id):
    all_lessons = sorted(Lesson.objects.filter(module_id=module_id), key=lambda x: x.id)
    return all_lessons[-1].id + 1 if all_lessons else 1


def get_module_in_course(course, module_id):
    return Module.objects.get(course=course, in_course_id=module_id)


def get_lesson_in_module(module, lesson_id):
    return Lesson.objects.get(module=module, in_module_id=lesson_id)


def pretty_lesson(lesson, user=None):
    timer = lesson['timer_set']
    files = lesson['lessonfiles_set']
    for i in range(len(timer)):
        obj = Timer.objects.get(id=timer[i])
        timer[i] = {"id": obj.id, "time": obj.time, "text": obj.text}
    for i in range(len(files)):
        files[i] = {"id": files[i], "file": LessonFiles.objects.get(id=files[i]).file.url}
    if user:
        homeworks = Homework.objects.filter(user=user, lesson_id=lesson['id'])
        if not homeworks:
            lesson['status'] = None
        elif homeworks.filter(status='Complete'):
            lesson['status'] = 'Complete'
        else:
            lesson['status'] = homeworks.last().status
    return lesson


def pretty_homework(homework):
    files = homework['homeworkfiles_set']
    for i in range(len(files)):
        files[i] = {"id": files[i], "file": HomeworkFiles.objects.get(id=files[i]).file.url}
    return homework


def get_timers(lesson):
    return Timer.objects.filter(lesson=lesson)


def get_files(lesson):
    return LessonFiles.objects.filter(lesson=lesson)


def get_notifiers(user):
    app = user.app
    return list(
        map(
            lambda sub: sub.user, CourseSubscription.objects.filter(course__user__app=app)
        )
    )


def count_progress(course: Course, user):
    _sum = 0
    all_lessons = 0
    completed_lessons = 0
    completed_modules = 0
    modules = Module.objects.filter(course=course)
    for module in modules:
        lessons = Lesson.objects.filter(module=module)
        comp = 0
        for lesson in lessons:
            all_lessons += 1
            try:
                if Homework.objects.filter(user=user, lesson=lesson, status='Complete'):
                    comp += 1
            except AttributeError:
                pass
        if comp == len(lessons):
            completed_modules += 1
        completed_lessons += comp
    return {
        "course_id": course.id,
        "course_name": course.name,
        "all_modules": len(modules),
        "completed_modules": completed_modules,
        "all_lessons": all_lessons,
        "completed_lessons": completed_lessons,
        "verdict": round(completed_lessons * 100 / all_lessons) if all_lessons else 0
    }


class Module(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False, verbose_name='Название', default="История Кочки")
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, blank=False, null=False)
    in_course_id = models.IntegerField(null=False, blank=False)
    image = models.ImageField(null=True, blank=True, upload_to="media/", verbose_name='Картинка')
    description = models.CharField(max_length=2000, null=False, blank=False, verbose_name='Название',
                                   default="Базовое описание (базированное)")

    class Meta:
        managed = True
        db_table = 'modules'


class Lesson(models.Model):
    image = models.ImageField(null=True, blank=False, upload_to="media/", verbose_name='Картинка')
    module = models.ForeignKey('courses.Module', on_delete=models.CASCADE, blank=False, null=False)
    video = models.FileField(null=True, blank=True, upload_to="media/", verbose_name='Видео')
    in_module_id = models.IntegerField(null=False, blank=False)
    name = models.CharField(max_length=1000, null=False, blank=False, verbose_name='Название')
    text = models.CharField(max_length=5000, null=False, blank=False, verbose_name='Описание')
    question = models.CharField(max_length=1000, null=False, blank=False, verbose_name='Задание')

    class Meta:
        managed = True
        db_table = 'lessons'


class LessonFiles(models.Model):
    lesson = models.ForeignKey('courses.Lesson', on_delete=models.CASCADE, blank=False, null=False)
    file = models.FileField(null=False, blank=False, upload_to="media/", verbose_name='Файл')

    class Meta:
        managed = True
        db_table = 'lessons_files'
        unique_together = ('lesson', 'file')


class Timer(models.Model):
    lesson = models.ForeignKey('courses.Lesson', on_delete=models.CASCADE, blank=False, null=False)
    time = models.TimeField(null=False, blank=False)
    text = models.CharField(max_length=1000, null=False, blank=False, verbose_name='Описание')

    class Meta:
        managed = True
        db_table = 'timers'
        unique_together = ('lesson', 'time')


class Special(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, blank=False, null=False)
    header = models.CharField(max_length=100, null=False, blank=False, verbose_name='Название')
    image = models.ImageField(null=True, blank=False, upload_to="media/", verbose_name='Картинка')
    description = models.CharField(max_length=2000, null=False, blank=False, verbose_name='Название',
                                   default="Базовое описание (базированное)")

    class Meta:
        managed = True
        db_table = 'special'


class Homework(models.Model):
    class Group(models.TextChoices):
        COMPLETE = 'Complete'
        IN_PROGRESS = 'In_progress'
        FAILED = 'Failed'

    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, blank=False, null=False)
    lesson = models.ForeignKey('courses.Lesson', on_delete=models.CASCADE, blank=False, null=False)
    text = models.CharField(max_length=5000, null=True, blank=True, verbose_name='Описание')
    status = models.CharField(
        max_length=20,
        choices=Group.choices,
        default=Group.IN_PROGRESS,
    )

    class Meta:
        managed = True
        db_table = 'homework'


class HomeworkFiles(models.Model):
    homework = models.ForeignKey('courses.Homework', on_delete=models.CASCADE, blank=False, null=False)
    file = models.FileField(null=False, blank=False, upload_to="media/", verbose_name='Файл')

    class Meta:
        managed = True
        db_table = 'homework_files'


class Calendar(models.Model):
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, blank=False, null=False)
    description = models.CharField(max_length=2000, null=False, blank=False, default="Базовое описание (базированное)")
    header = models.CharField(max_length=200, null=False, blank=False)
    date = models.DateField(null=False, blank=False, default="2021-01-01")
    time = models.TimeField(null=False, blank=False, default="00:00:00")
