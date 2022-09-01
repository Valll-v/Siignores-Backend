from rest_framework.serializers import ModelSerializer

from courses.models import *


class CourseSerializer(ModelSerializer):
    class Meta:
        model = Course
        fields = ('description', 'id', 'name', 'image', 'user')


class SpecialSerializer(ModelSerializer):
    class Meta:
        model = Special
        fields = ('description', 'id', 'header', 'image', 'user')


class GetModuleSerializer(ModelSerializer):
    class Meta:
        model = Module
        fields = ('description', 'id', 'name', 'in_course_id', 'image', 'course')


class PostModuleSerializer(ModelSerializer):
    class Meta:
        model = Module
        fields = ('description', 'name', 'in_course_id', 'image', 'course')


class PostLessonSerializer(ModelSerializer):
    class Meta:
        model = Lesson
        fields = ('module', 'image', 'video', 'in_module_id', 'name', 'text', 'question')


class GetLessonSerializer(ModelSerializer):
    class Meta:
        model = Lesson
        fields = ('id', 'module', 'image', 'video', 'in_module_id', 'name', 'text', 'question', 'timer_set',
                  'lessonfiles_set')


class PostTimingSerializer(ModelSerializer):
    class Meta:
        model = Timer
        fields = ('lesson', 'time', 'text')


class PostFileSerializer(ModelSerializer):
    class Meta:
        model = LessonFiles
        fields = ('lesson', 'file')


class GetTimingSerializer(ModelSerializer):
    class Meta:
        model = Timer
        fields = ('id', 'lesson', 'time', 'text')


class GetFileSerializer(ModelSerializer):
    class Meta:
        model = LessonFiles
        fields = ('id', 'lesson', 'file')


class HomeworkSerializer(ModelSerializer):
    class Meta:
        model = Homework
        fields = ('status', 'id', 'user', 'lesson', 'text', 'homeworkfiles_set')


class HomeworkFileSerializer(ModelSerializer):
    class Meta:
        model = HomeworkFiles
        fields = ('id', 'homework', 'file')


class CalendarSerializer(ModelSerializer):
    class Meta:
        model = Calendar
        fields = ('id', 'course', 'description', 'header', 'date', 'time')
