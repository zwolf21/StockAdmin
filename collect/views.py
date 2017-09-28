from pprint import pprint

from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, FormView, TemplateView, ListView, DetailView, DeleteView

# from .core import Collect
from .forms import *
from .models import Collect




class CollectListView(ListView):
    
    def get_queryset(self):
        collect = Collect()
        return collect.get_queryset()


class CollectDetailView(DetailView):
    template_name = 'collect/collect_detail.html'

    def get_object(self):
        collect = Collect()
        return collect.get(self.kwargs.get('slug'))

    def get_context_data(self, **kwargs):
        collect = Collect()
        context = super(CollectDetailView, self).get_context_data(**kwargs)
        context['object_list'] = collect.get_queryset()
        context['static'] = collect.get_static(**self.get_object())
        return context


class CollectFormView(FormView):
    template_name = 'collect/collect_form.html'
    success_url = '.'

    def get_form_class(self):
        return get_form_class(test=False, **self.kwargs)

    def form_valid(self, form):
        kind = self.kwargs.get('kind')
        collect = Collect()
        collect.save(test=True, auto_st=(kind=='ANY'), **form.cleaned_data)
        return super(CollectFormView, self).form_valid(form)

    def form_invalid(self, form):
        context = self.get_context_data()
        collect = Collect()
        Form = self.get_form_class()
        initial = collect.get_form_initial(**form.cleaned_data)
        print(initial)
        context['form'] = Form(initial)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        kind = self.kwargs.get('kind')
        collect = Collect()
        context = super(CollectFormView, self).get_context_data(**kwargs)
        context['object_list'] = collect.get_queryset()
        # Form = self.get_form_class() 
        # context['form'] = Form(initial = collect.get_form_initial(kind=kind, types=['ST']))
        return context



class StaticFormView(FormView):
    template_name = 'collect/static_form.html'
    success_url = '.'
 
    def get_form_class(self):
        return get_form_class(app='static', **self.kwargs)

    def form_valid(self, form):
        collect = Collect()
        collect.save_static(**form.cleaned_data)
        return super(StaticFormView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(StaticFormView, self).get_context_data(**kwargs)
        collect = Collect()
        Form = self.get_form_class()
        context['form'] = Form(initial=collect.get_static(**self.kwargs))
        context['object_list'] = collect.get_queryset()
        return context

class CollectDeleteView(DeleteView):
    # success_url = reverse_lazy('collect:create', args=('LABEl', ))

    def get_success_url(self):
        return reverse_lazy('collect:create', args=('LABEL',))

    def get_object(self):
        collect = Collect()
        return collect.get(self.kwargs.get('slug'))

    def delete(self, request, *args, **kwargs):
        collect = Collect()
        obj = self.get_object()
        collect.delete(obj.slug)
        return super(CollectDeleteView, self).delete(request, *args, **kwargs)


def clear(request):
    if request.method == "POST":
        collect = Collect()
        collect.clear()
    return HttpResponseRedirect(reverse('collect:create', args=('LABEL', )))











