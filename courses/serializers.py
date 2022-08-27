from rest_framework.serializers import ModelSerializer

from courses.models import Course, Module


class CourseSerializer(ModelSerializer):
    class Meta:
        model = Course
        fields = ('id', 'name', 'image', 'user')


class GetModuleSerializer(ModelSerializer):
    class Meta:
        model = Module
        fields = ('in_course_id', 'image', 'course')


class PostModuleSerializer(ModelSerializer):
    class Meta:
        model = Module
        fields = ('in_course_id', 'image', 'course')
