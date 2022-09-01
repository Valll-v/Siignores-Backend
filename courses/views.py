from django.http import JsonResponse

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from courses import models
from courses.models import CourseSubscription, Course, Module, pretty_lesson, Lesson, Special, Timer, LessonFiles, \
    pretty_homework, Homework, Calendar
from courses.serializers import CourseSerializer, PostModuleSerializer, GetModuleSerializer, PostLessonSerializer, \
    GetLessonSerializer, PostTimingSerializer, PostFileSerializer, SpecialSerializer, HomeworkSerializer, \
    HomeworkFileSerializer, CalendarSerializer
from chat.models import Chat, ChatUser, Notification
from loguru import logger
from users.models import CustomUser
from users.serializers import CustomUserProfileSerializer
import asyncio
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async


channel_layer = get_channel_layer()

def get_notifiers(user):
    app = user.app
    return list(set(list(
        map(
            lambda sub: sub.user, CourseSubscription.objects.filter(course__user__app=app)
        )
    )))


def notify(user_id, message):    
    logger.debug(f'sending notification to user {user_id}')
    Notification.objects.create(
        user_id=user_id,
        message=message
    )
    asyncio.run(channel_layer.group_send(
                'chat_' + str(user_id),
                {
                    'type': 'notify',
                    'message': message,
                    'notifications': 228
                }
            ))



class CourseViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @action(["post", "put"], detail=False)
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
            try:
                course.name = request.data['name']
            except KeyError:
                pass
            try:
                course.image = request.data['image']
            except KeyError:
                pass
            try:
                course.description = request.data['description']
            except KeyError:
                pass
            course.save()
            return Response(CourseSerializer(course).data)

    @action(["get"], detail=False)
    def course_get(self, request, course_id):
        try:
            user = request.user
            try:
                course = Course.objects.get(id=course_id)
            except Course.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid course id")
            except KeyError:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="Please, enter course_id (which equal id)")
            if course.user != user:
                return Response(status=status.HTTP_403_FORBIDDEN, data="Not your course")
        except AttributeError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid request")
        return Response(CourseSerializer(course).data)

    @action(["delete"], detail=False)
    def course_del(self, request, course_id):
        try:
            user = request.user
            try:
                course = Course.objects.get(id=course_id)
            except Course.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid course id")
            except KeyError:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="Please, enter course_id (which equal id)")
            if course.user != user:
                return Response(status=status.HTTP_403_FORBIDDEN, data="Not your course")
        except AttributeError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid request")
        course.delete()

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

    @action(["post", "put"], detail=False)
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
            try:
                request.data['in_course_id'] = models.set_module_id(course_id)
            except AttributeError:
                request.data._mutable = True
                request.data['in_course_id'] = models.set_module_id(course_id)
                request.data._mutable = False
            serializer = PostModuleSerializer(data=request.data)
            if serializer.is_valid(raise_exception=False):
                module = serializer.save()
            else:
                module = serializer.errors
                return Response(module)
            return Response(GetModuleSerializer(module).data)
        else:
            try:
                module = Module.objects.get(id=request.data["module"])
            except Module.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid module id")
            except KeyError:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="Please, enter module (which equal id)")
            try:
                module.name = request.data['name']
            except KeyError:
                pass
            try:
                module.image = request.data['image']
            except KeyError:
                pass
            try:
                module.description = request.data['description']
            except KeyError:
                pass
            module.save()
            return Response(GetModuleSerializer(module).data)

    @action(["get"], detail=False)
    def module_get(self, request, module_id):
        user = request.user
        try:
            module = Module.objects.get(id=module_id)
            course = module.course
        except Module.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid id")
        if course.user != user:
            return Response(status=status.HTTP_403_FORBIDDEN, data="You must be teacher of "
                                                                   "this course to get it")
        return Response(GetModuleSerializer(module).data)

    @action(["del"], detail=False)
    def module_del(self, request, module_id):
        user = request.user
        try:
            module = Module.objects.get(id=module_id)
            course = module.course
        except Module.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid id")
        if course.user != user:
            return Response(status=status.HTTP_403_FORBIDDEN, data="You must be teacher of "
                                                                   "this course to do that")
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

    @action(["get"], detail=False)
    def course_students(self, request, course_id):
        user = request.user
        try:
            course = Course.objects.get(id=course_id)
            subs = list(map(lambda x: x.user, CourseSubscription.objects.filter(course=course)))
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Please, enter course_id")
        except Course.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid id")
        if course.user != user:
            return Response(status=status.HTTP_403_FORBIDDEN, data="You must be teacher or student of "
                                                                   "this course to get it")
        return JsonResponse(
            list(
                map(
                    lambda x: CustomUserProfileSerializer(x).data, subs
                )
            ), safe=False
        )

    @action(["get"], detail=False)
    def student(self, request, student_id):
        user = request.user
        try:
            student = CustomUser.objects.get(id=student_id)
        except CustomUser.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid id")
        if student.app != user.app:
            return Response(status=status.HTTP_403_FORBIDDEN, data="That person not from your app")
        return Response(CustomUserProfileSerializer(student).data)

    @action(["get"], detail=False)
    def all_students(self, request):
        user = request.user
        if user.group != 'US':
            return Response(status=status.HTTP_403_FORBIDDEN, data="Stop do that, nasty hacker")
        return JsonResponse(
            list(
                map(
                    lambda x: CustomUserProfileSerializer(x).data, CustomUser.objects.filter(app=user.app, group='ST')
                )
            ), safe=False
        )

    @action(["get"], detail=False)
    def lesson_get(self, request, lesson_id):
        user = request.user
        try:
            lesson = Lesson.objects.get(id=lesson_id)
            course = lesson.module.course
            subs = list(map(lambda x: x.user, CourseSubscription.objects.filter(user=user, course=course)))
        except Module.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid id")
        if course.user != user and user not in subs:
            return Response(status=status.HTTP_403_FORBIDDEN, data="You must be teacher of "
                                                                   "this course to get it")
        return JsonResponse(pretty_lesson(GetLessonSerializer(lesson).data))

    @action(["get"], detail=False)
    def lesson_del(self, request, lesson_id):
        user = request.user
        try:
            lesson = Lesson.objects.get(id=lesson_id)
            course = lesson.module.course
        except Module.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid id")
        if course.user != user:
            return Response(status=status.HTTP_403_FORBIDDEN, data="You must be teacher of "
                                                                   "this course to get it")
        lesson.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(["post", "put"], detail=False)
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
            module = Module.objects.get(id=request.data["module"])
        except Module.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid module id")
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Please, enter module (which equal id)")
        if request.method == 'POST':
            try:
                request.data['in_module_id'] = models.set_lesson_id(module.id)
            except AttributeError:
                request.data._mutable = True
                request.data['in_module_id'] = models.set_lesson_id(module.id)
                request.data._mutable = False
            serializer = PostLessonSerializer(data=request.data)
            if serializer.is_valid(raise_exception=False):
                lesson = serializer.save()
                try:
                    if "timer" in request.data:
                        try:
                            list_ = request.data.getlist('timer')
                        except AttributeError:
                            list_ = request.data['timer']
                        for i in list_:
                            timer_serializer = PostTimingSerializer(data={
                                'lesson': lesson.id,
                                'time': i.split()[0],
                                'text': i[i.index(' '):]
                            })
                            if timer_serializer.is_valid(raise_exception=False):
                                timer_serializer.save()
                            else:
                                timer = timer_serializer.errors
                                lesson.delete()
                                return Response(timer)
                    if "lesson_file" in request.data:
                        try:
                            list_ = request.data.getlist('lesson_file')
                        except AttributeError:
                            list_ = request.data['lesson_file']
                        for i in list_:
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
            resp = JsonResponse(lesson)
            resp['Access-Control-Allow-Origin'] = '*'
            return resp
        else:
            try:
                lesson = Lesson.objects.get(id=request.data["lesson"])
            except Lesson.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid lesson id")
            except KeyError:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="Please, enter lesson (which equal id)")
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
                try:
                    list_ = request.data.getlist('timer')
                except AttributeError:
                    list_ = request.data['timer']
                for i in list_:
                    timer_serializer = PostTimingSerializer(data={
                        'lesson': lesson.id,
                        'time': i.split()[0],
                        'text': i[i.index(' '):]
                    })
                    if timer_serializer.is_valid(raise_exception=False):
                        timer_serializer.save()
                    else:
                        timer = timer_serializer.errors
                        return Response(timer)
            if "lesson_file" in request.data:
                for i in models.get_files(lesson):
                    i.delete()
                try:
                    list_ = request.data.getlist('lesson_file')
                except AttributeError:
                    list_ = request.data['lesson_file']
                for i in list_:
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
            resp = JsonResponse(lesson)
            resp['Access-Control-Allow-Origin'] = '*'
            return resp

    @action(["post", "put"], detail=False)
    def special(self, request):
        user = request.user
        if request.method == 'POST':
            try:
                request.data['user'] = user.id
            except AttributeError:
                request.data._mutable = True
                request.data['user'] = user.id
                request.data._mutable = False
            serializer = SpecialSerializer(data=request.data)
            if serializer.is_valid():
                special = serializer.save()
            else:
                special = serializer.errors
                return Response(special)
            return Response(SpecialSerializer(special).data)
        else:
            try:
                special = Special.objects.get(id=request.data["special_id"])
            except Course.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid special id")
            except KeyError:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="Please, enter special_id (which equal id)")
            if special.user != user:
                return Response(status=status.HTTP_403_FORBIDDEN, data="Not your course")
            try:
                special.header = request.data['header']
            except KeyError:
                pass
            try:
                special.image = request.data['image']
            except KeyError:
                pass
            try:
                special.description = request.data['description']
            except KeyError:
                pass
            special.save()
            return Response(SpecialSerializer(special).data)

    @action(["get"], detail=False)
    def special_get(self, request, special_id):
        try:
            special = Special.objects.get(id=special_id)
        except Special.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid id")
        return Response(SpecialSerializer(special).data)

    @action(["delete"], detail=False)
    def special_del(self, request, special_id):
        user = request.user
        try:
            special = Special.objects.get(id=special_id)
        except Special.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid id")
        if special.user != user:
            return Response(status=status.HTTP_403_FORBIDDEN,
                            data="You are simp student, get away. Or that not your app, get away anyway")
        special.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(["get"], detail=False)
    def special_list(self, request):
        app = request.user.app
        try:
            specials = Special.objects.filter(user__in=CustomUser.objects.filter(group='US', app=app))
        except Special.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid id")
        return Response(SpecialSerializer(special).data for special in specials)

    @action(["post"], detail=False)
    def add_timer(self, request, lesson_id):
        user = request.user
        try:
            lesson = Lesson.objects.get(id=lesson_id)
            course = lesson.module.course
        except Lesson.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid lesson id")
        if course.user != user:
            return Response(status=status.HTTP_403_FORBIDDEN, data="You must be teacher of "
                                                                   "this course to get it")
        if "timer" in request.data:
            try:
                list_ = request.data.getlist('timer')
            except AttributeError:
                list_ = request.data['timer']
            for i in list_:
                timer_serializer = PostTimingSerializer(data={
                    'lesson': lesson.id,
                    'time': i.split()[0],
                    'text': i[i.index(' '):]
                })
                if timer_serializer.is_valid(raise_exception=False):
                    timer_serializer.save()
                else:
                    timer = timer_serializer.errors
                    return Response(timer)
        return JsonResponse(pretty_lesson(GetLessonSerializer(lesson).data))

    @action(["post"], detail=False)
    def add_files(self, request, lesson_id):
        user = request.user
        try:
            lesson = Lesson.objects.get(id=lesson_id)
            course = lesson.module.course
        except Lesson.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid lesson id")
        if course.user != user:
            return Response(status=status.HTTP_403_FORBIDDEN, data="You must be teacher of "
                                                                   "this course to do that")
        if "lesson_file" in request.data:
            try:
                list_ = request.data.getlist('lesson_file')
            except AttributeError:
                list_ = request.data['lesson_file']
            for i in list_:
                file_serializer = PostFileSerializer(data={
                    'lesson': lesson.id,
                    'file': i
                })
                if file_serializer.is_valid(raise_exception=False):
                    file_serializer.save()
                else:
                    file = file_serializer.errors
                    return Response(file)
        return JsonResponse(pretty_lesson(GetLessonSerializer(lesson).data))

    @action(["delete"], detail=False)
    def delete_timer(self, request, timer_id):
        user = request.user
        try:
            timer = Timer.objects.get(id=timer_id)
            course = timer.lesson.module.course
        except Timer.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid Timer id")
        if course.user != user:
            return Response(status=status.HTTP_403_FORBIDDEN, data="You must be teacher of "
                                                                   "this course to do that")
        timer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(["delete"], detail=False)
    def delete_file(self, request, file_id):
        user = request.user
        try:
            file = LessonFiles.objects.get(id=file_id)
            course = file.lesson.module.course
        except LessonFiles.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid LessonFiles id")
        if course.user != user:
            return Response(status=status.HTTP_403_FORBIDDEN, data="You must be teacher of "
                                                                   "this course to do that")
        file.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(["post"], detail=False)
    def add_homework(self, request):
        user = request.user
        try:
            lesson = Lesson.objects.get(id=request.data["lesson"])
            course = lesson.module.course
            subs = list(map(lambda x: x.user, CourseSubscription.objects.filter(user=user, course=course)))
        except Module.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid id")
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Please, enter lesson (which equal id)")
        if user not in subs:
            return Response(status=status.HTTP_403_FORBIDDEN, data="You must be sub on course to do that")
        try:
            request.data['user'] = user.id
        except AttributeError:
            request.data._mutable = True
            request.data['user'] = user.id
            request.data._mutable = False
        serializer = HomeworkSerializer(data=request.data)
        if serializer.is_valid():
            homework = serializer.save()
        else:
            homework = serializer.errors
            return Response(homework)
        if "files" in request.data:
            try:
                list_ = request.data.getlist('files')
            except AttributeError:
                list_ = request.data['files']
            for i in list_:
                file_serializer = HomeworkFileSerializer(data={
                    'homework': homework.id,
                    'file': i
                })
                if file_serializer.is_valid(raise_exception=False):
                    file_serializer.save()
                else:
                    file = file_serializer.errors
                    return Response(file)
        return JsonResponse(pretty_homework(HomeworkSerializer(homework).data))

    @action(["put"], detail=False)
    def check_homework(self, request):
        user = request.user
        try:
            homework = Homework.objects.get(id=request.data["homework"])
            course = homework.lesson.module.course
        except Homework.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid id")
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Please, enter homework (which equal id)")
        if user != course.user:
            return Response(status=status.HTTP_403_FORBIDDEN, data="You must be teacher on course to do that")
        if "homework_status" in request.data:
            print(Homework.Group.values)
            if request.data["homework_status"] in Homework.Group.values:
                homework.status = request.data["homework_status"]
                homework.save()
                return JsonResponse(pretty_homework(HomeworkSerializer(homework).data))
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data="Invalid verdict (homework_status), make your choice between Complete and Failed")
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Please, write your verdict (homework_status)")

    @action(["get"], detail=False)
    def get_all_homework_by_course(self, request, course_id):
        user = request.user
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid id")
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Please, enter Course (which equal id)")
        if user != course.user:
            return Response(status=status.HTTP_403_FORBIDDEN, data="You must be teacher on course to do that")
        return JsonResponse(
            {
                "homeworks": [
                    pretty_homework(HomeworkSerializer(homework).data) for homework in
                    Homework.objects.filter(lesson__module__course=course)
                ]
            }
        )

    @action(["get"], detail=False)
    def get_all_homework_by_module(self, request, module_id):
        user = request.user
        try:
            module = Module.objects.get(id=module_id)
            course = module.course
        except Course.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid id")
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Please, enter module (which equal id)")
        if user != course.user:
            return Response(status=status.HTTP_403_FORBIDDEN, data="You must be teacher on course to do that")
        return JsonResponse(
            {
                "homeworks": [
                    pretty_homework(HomeworkSerializer(homework).data) for homework in
                    Homework.objects.filter(lesson__module=module)
                ]
            }
        )

    @action(["get"], detail=False)
    def get_all_homework_by_lesson(self, request, lesson_id):
        user = request.user
        try:
            lesson = Lesson.objects.get(id=lesson_id)
            course = lesson.module.course
        except Course.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid id")
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Please, enter lesson (which equal id)")
        if user != course.user:
            return Response(status=status.HTTP_403_FORBIDDEN, data="You must be teacher on course to do that")
        return JsonResponse(
            {
                "homeworks": [
                    pretty_homework(HomeworkSerializer(homework).data) for homework in
                    Homework.objects.filter(lesson=lesson)
                ]
            }
        )

    @action(["get"], detail=False)
    def get_all_homework(self, request):
        user = request.user
        app = user.app
        if user.group == 'ST':
            return Response(status=status.HTTP_403_FORBIDDEN, data="You must be user of app to do that")
        return JsonResponse(
            {
                "homeworks": [
                    pretty_homework(HomeworkSerializer(homework).data) for homework in
                    Homework.objects.filter(user__app=app)
                ]
            }
        )

    @action(["get"], detail=False)
    def get_target_homework(self, request, homework_id):
        try:
            homework = Homework.objects.get(id=homework_id)
        except Homework.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid id")
        return JsonResponse(pretty_homework(HomeworkSerializer(homework).data))

    @action(["get"], detail=False)
    def progress(self, request):
        user = request.user
        progress = []
        for sub in CourseSubscription.objects.filter(user=user):
            course = sub.course
            progress.append(models.count_progress(course, user))
        return Response(progress)

    @action(["post", "put"], detail=False)
    def calendar(self, request):
        user = request.user
        try:
            course = Course.objects.get(id=request.data["course"])
        except Course.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid id")
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Please, enter Course (which equal id)")
        if user != course.user:
            return Response(status=status.HTTP_403_FORBIDDEN, data="You must be teacher on course to do that")
        if request.method == 'POST':
            try:
                request.data['user'] = user.id
            except AttributeError:
                request.data._mutable = True
                request.data['user'] = user.id
                request.data._mutable = False
            serializer = CalendarSerializer(data=request.data)
            if serializer.is_valid():
                cal = serializer.save()
                for notifyee in get_notifiers(user):
                    notify(notifyee.id, 'Новое событие! Посмотрите календарь!')
                return Response(CalendarSerializer(cal).data)
            else:
                cal = serializer.errors
                return Response(cal)
        else:
            try:
                calendar = Calendar.objects.get(id=request.data["calendar"])
            except Calendar.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid calendar id")
            except KeyError:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="Please, enter calendar_id (which equal id)")
            if calendar.course.user != user:
                return Response(status=status.HTTP_403_FORBIDDEN, data="Not your course")
            try:
                calendar.header = request.data['header']
            except KeyError:
                pass
            try:
                calendar.description = request.data['description']
            except KeyError:
                pass
            try:
                calendar.datetime = request.data['datetime']
            except KeyError:
                pass
            calendar.save()
            for notifyee in get_notifiers(user):
                asyncio.run(notify(notifyee.id, f'Изменено событие {calendar.header}!'))
            return Response(CalendarSerializer(calendar).data)

    @action(["get"], detail=False)
    def get_calendar(self, request, calendar_id):
        try:
            calendar = Calendar.objects.get(id=calendar_id)
        except Calendar.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid calendar id")
        return Response(CalendarSerializer(calendar).data)

    @action(["delete"], detail=False)
    def delete_calendar(self, request, calendar_id):
        user = request.user
        try:
            calendar = Calendar.objects.get(id=calendar_id)
        except Calendar.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid calendar id")
        if calendar.course.user != user:
            return Response(status=status.HTTP_403_FORBIDDEN, data="Not your course")
        calendar.delete()
        for notifyee in get_notifiers(user):
            asyncio.run(notify(notifyee.id,  f'Отменено событие {calendar.header}!'))
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(["get"], detail=False)
    def student_calendar(self, request):
        user = request.user
        try:
            courses = [i.course for i in CourseSubscription.objects.filter(user=user)]
            calendars = Calendar.objects.filter(course__in=courses)
        except Calendar.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid calendar id")
        return Response([CalendarSerializer(calendar).data for calendar in calendars])
