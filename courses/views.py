from django.http import JsonResponse

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from courses import models
from courses.models import CourseSubscription, Course, Module, pretty_lesson, Lesson
from courses.serializers import CourseSerializer, PostModuleSerializer, GetModuleSerializer, PostLessonSerializer, \
    GetLessonSerializer, PostTimingSerializer, PostFileSerializer
from chat.models import Chat, ChatUser
from loguru import logger
from users.models import CustomUser


class CourseViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @action(["post", "put", "delete", "gets"], detail=False)
    def course(self, request):
        if request.method == "POST":
            try:
                user = request.user
                if user.group != "US":
                    return Response(status=status.HTTP_403_FORBIDDEN, data="Only for teachers")
                request.data._mutable = True
                request.data['user'] = user.id
                request.data._mutable = False
                serializer = CourseSerializer(data=request.data)
                if serializer.is_valid():
                    logger.debug('entered')
                    course = serializer.save()
                    chat = Chat.objects.create(
                        name=course.name,
                        course_id=course.id
                    )
                    ChatUser.objects.create(
                        user_id=user.id,
                        chat_id=chat.id
                    )
                else:
                    course = serializer.errors
                    return Response(course)
                return Response(CourseSerializer(course).data)
            except AttributeError:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid request")
        else:
            try:
                user = request.user
                try:
                    course = Course.objects.get(id=request.data["course_id"])
                except Course.DoesNotExist:
                    return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid course id")
                except KeyError:
                    return Response(status=status.HTTP_400_BAD_REQUEST, data="Please, enter course_id (which equal id)")
                if course.user != user:
                    return Response(status=status.HTTP_403_FORBIDDEN, data="Not your course")
            except AttributeError:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid request")
            if request.method == 'PUT':
                try:
                    course.name = request.data['name']
                except KeyError:
                    pass
                try:
                    course.image = request.data['image']
                except KeyError:
                    pass
                course.save()
                return Response(CourseSerializer(course).data)
            elif request.method == 'GET':
                return Response(CourseSerializer(course).data)
            else:
                course.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

    @action(["post"], detail=False)
    def sub_course(self, request):
        user = request.user
        try:
            course = Course.objects.get(id=request.data["course_id"])
        except Course.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid course id")
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Please, enter course_id (which equal id)")
        if course.user != user:
            return Response(status=status.HTTP_403_FORBIDDEN, data="Not your course")
        try:
            CustomUser.objects.get(id=request.data["user_id"])
            CourseSubscription.objects.get(user_id=request.data["user_id"], course_id=request.data["course_id"])
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Bad request (already sub on this course)")
        except CustomUser.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid user_id")
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Please, enter user_id (which equal id)")
        except CourseSubscription.DoesNotExist:
            try:
                sub = CourseSubscription(
                    course_id=request.data["course_id"],
                    user_id=request.data["user_id"]
                )
                sub.save()
                chat = Chat.objects.get(course_id=request.data["course_id"])
                ChatUser.objects.create(
                    user_id=request.data["user_id"],
                    chat_id=chat.id
                )
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

    @action(["post", "put", "delete", "get"], detail=False)
    def module(self, request):
        user = request.user
        try:
            course_id = request.data['course']
            course = Course.objects.get(id=request.data["course"])
        except Course.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid course id")
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Please, enter course (which equal id)")
        if course.user != user:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Not your course")
        if request.method == "POST":
            request.data['in_course_id'] = models.set_module_id(course_id)
            serializer = PostModuleSerializer(data=request.data)
            if serializer.is_valid(raise_exception=False):
                module = serializer.save()
            else:
                module = serializer.errors
                return Response(module)
            return Response(GetModuleSerializer(module).data)
        else:
            try:
                module = models.get_module_in_course(course, request.data['module'])
            except Module.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid module id")
            except KeyError:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="Please, enter module (which equal id)")
            if request.method == 'PUT':
                try:
                    module.name = request.data['name']
                except KeyError:
                    pass
                try:
                    module.image = request.data['image']
                except KeyError:
                    pass
                module.save()
                return Response(GetModuleSerializer(module).data)
            elif request.method == 'GET':
                return Response(GetModuleSerializer(module).data)
            else:
                module.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

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

    @action(["get"], detail=False)
    def get_lessons(self, request, module_id):
        user = request.user
        try:
            module = Module.objects.get(id=module_id)
            course = module.course
            subs = list(map(lambda x: x.user, CourseSubscription.objects.filter(user=user, course=course)))
            lessons = Lesson.objects.filter(module=module)
        except Module.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid id")
        if course.user != user and user not in subs:
            return Response(status=status.HTTP_403_FORBIDDEN, data="You must be teacher or student of "
                                                                   "this course to get it")
        return JsonResponse(
            list(map(lambda lesson: pretty_lesson(GetLessonSerializer(lesson).data), lessons)), safe=False
        )

    @action(["post", "put", "delete", "get"], detail=False)
    def lesson(self, request):
        user = request.user
        try:
            course = Course.objects.get(id=request.data["course"])
        except Course.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid course id")
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Please, enter course (which equal id)")
        if course.user != user:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Not your course")
        try:
            module = models.get_module_in_course(course, request.data['module'])
        except Module.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid module id")
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Please, enter module (which equal id)")
        if request.method == 'POST':
            request.data['in_module_id'] = models.set_lesson_id(module.id)
            serializer = PostLessonSerializer(data=request.data)
            if serializer.is_valid(raise_exception=False):
                lesson = serializer.save()
                try:
                    if "timer" in request.data:
                        for i in request.data.getlist('timer'):
                            timer_serializer = PostTimingSerializer(data={
                                'lesson': lesson.id,
                                'time': i.split()[0],
                                'text': i.split()[1]
                            })
                            if timer_serializer.is_valid(raise_exception=False):
                                timer_serializer.save()
                            else:
                                timer = timer_serializer.errors
                                lesson.delete()
                                return Response(timer)
                    if "lesson_file" in request.data:
                        for i in request.data.getlist('lesson_file'):
                            file_serializer = PostFileSerializer(data={
                                'lesson': lesson.id,
                                'file': i
                            })
                            if file_serializer.is_valid(raise_exception=False):
                                file_serializer.save()
                            else:
                                file = file_serializer.errors
                                lesson.delete()
                                return Response(file)
                except Exception as ex:
                    return Response(status=status.HTTP_400_BAD_REQUEST, data=f"Invalid timer, {ex}")
            else:
                lesson = serializer.errors
                return Response(lesson)
            lesson = pretty_lesson(GetLessonSerializer(lesson).data)
            return JsonResponse(lesson)
        else:
            try:
                lesson = models.get_lesson_in_module(module, request.data['lesson'])
            except Lesson.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid lesson id")
            except KeyError:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="Please, enter lesson (which equal id)")
            if request.method == 'DELETE':
                lesson.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            elif request.method == 'GET':
                lesson = pretty_lesson(GetLessonSerializer(lesson).data)
                return JsonResponse(lesson)
            else:
                try:
                    lesson.image = request.data["image"]
                except KeyError:
                    pass
                try:
                    lesson.name = request.data["name"]
                except KeyError:
                    pass
                try:
                    lesson.text = request.data["text"]
                except KeyError:
                    pass
                try:
                    lesson.video = request.data["video"]
                except KeyError:
                    pass
                try:
                    lesson.question = request.data["question"]
                except KeyError:
                    pass
                if "timer" in request.data:
                    for i in models.get_timers(lesson):
                        i.delete()
                    for i in request.data.getlist('timer'):
                        timer_serializer = PostTimingSerializer(data={
                              'lesson': lesson.id,
                            'time': i.split()[0],
                            'text': i.split()[1]
                        })
                        if timer_serializer.is_valid(raise_exception=False):
                            timer_serializer.save()
                        else:
                            timer = timer_serializer.errors
                            return Response(timer)
                if "lesson_file" in request.data:
                    for i in models.get_files(lesson):
                        i.delete()
                    for i in request.data.getlist('lesson_file'):
                        file_serializer = PostFileSerializer(data={
                            'lesson': lesson.id,
                            'file': i
                        })
                        if file_serializer.is_valid(raise_exception=False):
                            file_serializer.save()
                        else:
                            file = file_serializer.errors
                            return Response(file)
            lesson.save()
            lesson = pretty_lesson(GetLessonSerializer(lesson).data)
            return JsonResponse(lesson)

