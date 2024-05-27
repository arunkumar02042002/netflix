from typing import Any
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import TemplateView, ListView, DetailView
from django.views import View
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.conf import settings
from django.core.serializers import serialize
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Prefetch

from .models import Movie, MovieWishList, Like, Comment
from .forms import CommentForm

import json
import re

# Create your views here.
class IndexView(TemplateView):
    template_name = 'main/index.html'

class AddRemoveWhislistView(View):

    def post(self, request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            return JsonResponse({
                "error":True,
                "message":"User is not authenticated!",
                "data":{}
            }, status=400)
        
        movie = Movie.objects.filter(slug=kwargs['slug']).first()

        if not movie:
            return JsonResponse({
                "error":True,
                "message":"Invalid Slug field!",
                "data":{}
            }, status=404)
        
        obj, created = MovieWishList.objects.get_or_create(user=user, movie=movie)

        if not created:
            obj.delete()
            return JsonResponse({
                "error":False,
                "message":"Added to your wishlist!",
                "data":{
                    'in_wishlist':created
                }
            })

        return JsonResponse({
            "error":False,
            "message":"Added to your wishlist!",
            "data":{
                'in_wishlist':created
            }
        })


class MovieDetailView(LoginRequiredMixin, DetailView):
    template_name = 'main/movie_detail.html'
    queryset = Movie.objects.all()
    context_object_name = "movie"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.object = self.get_object()

        with transaction.atomic():
            self.object.views += 1
            self.object.save()

        context = self.get_context_data(object=self.object)

        instance = MovieWishList.objects.filter(user=request.user, movie=self.object)
        
       # Check if the requested user has liked the movie
        user = self.request.user
        context['has_liked'] = Like.objects.filter(user=user, movie=self.object).exists()

        # Check if the requested user has added the movie to their wishlist
        context['in_wishlist'] = MovieWishList.objects.filter(user=user, movie=self.object).exists()

        # Add comments context
        context['comments'] = self.object.comments.all().order_by('-created_at')[:10]

        return self.render_to_response(context)
    
    def get_object(self, queryset = None):
        movie = self.queryset.filter(slug=self.kwargs["slug"]).prefetch_related(Prefetch("comments", queryset=Comment.objects.order_by("-created_at").select_related("user"))).first()
        if movie is None:
            raise Http404("Not Found")
        return movie


class MovieListView(LoginRequiredMixin, ListView):
    queryset = Movie.objects.all()
    paginate_by = 3
    context_object_name = "movies"
    template_name = "main/movie_list.html"

    def get_queryset(self) -> QuerySet[Any]:
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        ordering = self.request.GET.get('ordering', '-ratings')
        genre = self.request.GET.get('genre', '')

        filter_condition = Q()
        if q: 
            filter_condition |= Q(title__icontains=q)
            filter_condition |= Q(director__iexact=q)
            queryset = queryset.filter(filter_condition)

        if genre:
            queryset = queryset.filter(genre__iexact=genre)

        queryset = queryset.order_by(ordering)
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        query_params = re.sub(r'page=\d&', '', self.request.GET.urlencode()) # Capture current query parameters
        query_params = re.sub(r'page=\d', '', query_params)
        context['query_params'] = query_params
        return context

class MovieListApiView(View):
    querset = Movie.objects.all()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serialized = serialize('json', queryset=queryset[:10])

        return JsonResponse({
            "error":False,
            "movies": json.loads(serialized)
        }, status=200)
    
    def get_queryset(self):
        queryset = self.querset
        q = self.request.GET.get('q')

        filter_condition = Q()
        if q: 
            filter_condition |= Q(title__icontains=q)
            filter_condition |= Q(director__iexact=q)
            filter_condition |= Q(genre__iexact=q)
            queryset = queryset.filter(filter_condition)
        else:
            queryset = Movie.objects.none()
        return queryset
    

class MovieLikeAndDislikeView(LoginRequiredMixin, View):
    
    def post(self, request, slug, *args, **kwargs):
        movie = Movie.objects.filter(slug=slug).first()

        if not movie:
            return JsonResponse({
                "error":True,
                "message":"Invalid slug field!",
                "data":{},
            }, status=404)
        
        instance, created = Like.objects.get_or_create(user=request.user, movie=movie)

        if created:
            with transaction.atomic():
                movie.like_counts += 1
                movie.save()

            return JsonResponse({
                "error":False,
                "message":"Movie liked!",
                "data":{
                    'has_liked':True,
                    'like_counts':movie.like_counts
                }
            })
        
        instance.delete()
        with transaction.atomic():
            movie.like_counts -= 1
            movie.save()

        return JsonResponse({
                "error":False,
                "message":"Movie disliked!",
                "data":{
                    'has_liked':False,
                    'like_counts':movie.like_counts
                }
            })


class AddCommentToMovieView(LoginRequiredMixin, View):
    form_class = CommentForm
    
    def post(self, request, *args, **kwargs):


        slug = kwargs['slug']

        movie = Movie.objects.filter(slug=slug).first()

        if not movie:
            return JsonResponse({
                "error":True,
                "movie":"Invalid slug field",
                "data":{},
            }, status=404)
        
        user = request.user
        form = self.form_class({'value':request.POST.get('comment')})


        if form.is_valid() is False:
            return JsonResponse({
                "error":True,
                "message":form.errors.pop('value')[0],
                "data":{}
            }, status=400)
        
        comment = Comment.objects.create(user=user, movie=movie, value=form.cleaned_data['value'])

        return JsonResponse({
            "error":False,
            "mesage":"Successfully added!",
            "data":{
                'user':user.username,
                'comment':json.loads(serialize('json', [comment]))[0],
            }
        }, status=201)
    

class WishlistListView(ListView):
    paginate_by = 3
    context_object_name = 'movies'

    def get(self, request, *args, **kwargs):

        if not request.user.is_authenticated:
            return JsonResponse({
                "error":True,
                "message": "User is not authenticated.",
                "data": {}
            })
            
        response = super().get(request, *args, **kwargs)
        movies_serialized = serialize('json', response.context_data['movies'])
        page_obj = response.context_data["page_obj"]

        # previous
        if page_obj.has_previous(): previous = page_obj.previous_page_number()
        else: previous = ""

        # next
        if page_obj.has_next(): next = page_obj.next_page_number()
        else: next = ""

        return JsonResponse({
            "error":False,
            "message": "",
            "data": {
                "count": page_obj.paginator.count,
                "previous": previous,
                "next": next,
                "results": json.loads(movies_serialized)
            }
        })

    def get_queryset(self) -> QuerySet[Any]:
        user = self.request.user
        return Movie.objects.filter(wishlist_users__user=user)
    