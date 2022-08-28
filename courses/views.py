from django.http import JsonResponse

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from courses import models
from courses.models import CourseSubscription, Course, Module
from courses.serializers import CourseSerializer, PostModuleSerializer, GetModuleSerializer


class CourseViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @action(["post"], detail=False)
    def add_course(self, request):
        try:
            user = request.user
            if user.group != "US":
                return Response(status=status.HTTP_403_FORBIDDEN, data="Only for teachers")
            request.data._mutable = True
            request.data['user'] = user.id
            request.data._mutable = False
            serializer = CourseSerializer(data=request.data)
            if serializer.is_valid():
                course = serializer.save()
            else:
                course = serializer.errors
                return Response(course)
            return Response(CourseSerializer(course).data)
        except AttributeError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid request")

    @action(["post"], detail=False)
    def sub_course(self, request):
        user = request.user
        if user.group != "ST":
            return Response(status=status.HTTP_403_FORBIDDEN, data="Only for students")
        try:
            CourseSubscription.objects.get(user=user, course_id=request.data["course_id"])
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Bad request (already sub on this course)")
        except CourseSubscription.DoesNotExist:
            try:
                sub = CourseSubscription(
                    course_id=request.data["course_id"],
                    user=request.data["user_id"]
                )
                sub.save()
            except KeyError:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="Bad request (must contain course_id and )")
            return Response(CourseSerializer(sub.course).data)

    @action(["get"], detail=False)
    def get_courses(self, request):
        user = request.user
        if user.group == "ST":
            subs = CourseSubscription.objects.filter(user=user)
            return JsonResponse(
                list(map(lambda sub: CourseSerializer(sub.course).data, subs)), safe=False
            )
        elif user.group == "US":
            courses = Course.objects.filter(user=user)
            return JsonResponse(
                list(map(lambda course: CourseSerializer(course).data, courses)), safe=False
            )
        else:
            Response(status=status.HTTP_403_FORBIDDEN, data="Admin can't had courses")

    @action(["post"], detail=False)
    def add_module(self, request):
        user = request.user
        try:
            course_id = request.data['course']
            course = Course.objects.get(id=request.data["course"])
        except Course.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid id")
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Please, enter course (which equal id)")
        if course.user != user:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Not your course")
        request.data['in_course_id'] = models.set_module_id(course_id)
        serializer = PostModuleSerializer(data=request.data)
        if serializer.is_valid(raise_exception=False):
            module = serializer.save()
        else:
            module = serializer.errors
            return Response(module)
        return Response(GetModuleSerializer(module).data)

    @action(["get"], detail=False)
    def get_modules(self, request, course_id):
        user = request.user
        try:
            course = Course.objects.get(id=course_id)
            subs = list(map(lambda x: x.user, CourseSubscription.objects.filter(user=user, course=course)))
            modules = Module.objects.filter(course=course)
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Please, enter course_id")
        except Course.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid id")
        if course.user != user and user not in subs:
            return Response(status=status.HTTP_403_FORBIDDEN, data="You must be teacher or student of "
                                                                   "this course to get it")
        return JsonResponse(
            list(map(lambda module: GetModuleSerializer(module).data, modules)), safe=False
        )
