from rest_framework.serializers import ModelSerializer

from courses.models import Course, Module, Lesson, Timer, LessonFiles


class CourseSerializer(ModelSerializer):
    class Meta:
        model = Course
        fields = ('id', 'name', 'image', 'user')


class GetModuleSerializer(ModelSerializer):
    class Meta:
        model = Module
        fields = ('id', 'name', 'in_course_id', 'image', 'course')


class PostModuleSerializer(ModelSerializer):
    class Meta:
        model = Module
        fields = ('name', 'in_course_id', 'image', 'course')


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
