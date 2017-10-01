from pprint import pprint

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, FormView, TemplateView, ListView, DetailView, DeleteView
from django.conf import settings

# from .core import Collect
from .forms import CollectForm, CollectFormset, ConfigForm, FORMSET_INITIAL
from .apis import Collector, save_collect, set_form_initial, guess_time_range




class CollectDetailView(DetailView):
    template_name = 'collect/collect_detail.html'

    def get_object(self):
        c = Collector()
        return c.get_object(self.kwargs.get('slug'))

    def get_context_data(self, **kwargs):
        kind = self.kwargs.get('kind')
        c = Collector()
        context = super(CollectDetailView, self).get_context_data(**kwargs)
        context['object_list'] = c.get_queryset()
        context['config'] = c.get_config(kinds=[kind])
        context['objects'] = c.get_parsed(self.get_object().get('slug'))
        return context


class CollectFormView(FormView):
    template_name = 'collect/collect_form.html'
    success_url = '.'
    form_class = CollectForm


    def form_valid(self, form):
        obj = save_collect(form.cleaned_data, test=settings.TEST)
        self.success_url = reverse('collect:detail', args=(obj['slug'],))
        return super(CollectFormView, self).form_valid(form)


    def get_context_data(self, **kwargs):
        kind = self.kwargs.get('kind')
        Form = self.get_form_class()
        Form.base_fields['kinds'].initial = [kind]
        c = Collector()
        context = super(CollectFormView, self).get_context_data(**kwargs)
        context['object_list'] = c.get_queryset()
        context['form'] = Form()
        return context



class ConfigFormView(FormView):
    template_name = 'collect/config_form.html'
    success_url = reverse_lazy('collect:create', args=('LABEL',))
    form_class = ConfigForm

    def form_valid(self, form):
        c = Collector()
        c.config.save(**form.cleaned_data)
        return super(ConfigFormView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ConfigFormView, self).get_context_data(**kwargs)
        kind = self.kwargs.get('kind')
        c = Collector()
        Form = self.get_form_class()
        context['form'] = Form(initial=c.config.as_put(kind))
        context['object_list'] = c.get_queryset()
        return context


class CollectDeleteView(DeleteView):
    # success_url = reverse_lazy('collect:create', args=('LABEl', ))

    def get_success_url(self):
        return reverse_lazy('collect:create', args=('LABEL',))

    def get_object(self):
        c = Collector()
        return c.get_object(self.kwargs.get('slug'))

    def delete(self, request, *args, **kwargs):
        c = Collector()
        obj = self.get_object()
        c.delete(obj.slug)
        return super(CollectDeleteView, self).delete(request, *args, **kwargs)


def clear(request):
    if request.method == "POST":
        c = Collector()
        c.clear()
    return HttpResponseRedirect(reverse('collect:create', args=('LABEL', )))


class CollectBatchFormView(FormView):
    template_name = 'collect/collect_form.html'
    success_url = '.'
    form_class = CollectForm

    def get_context_data(self, **kwargs):
        context = super(CollectBatchFormView, self).get_context_data(**kwargs)
        context['formset'] = CollectFormset(self.request.POST or None, initial=FORMSET_INITIAL)
        Form = self.get_form_class()
        context['form'] = Form(self.request or None)
        c = Collector()
        context['object_list'] = c.get_queryset()
        return context

    # 폼셋 을 다룰땐 form_invalid 여기서 하는게...
    def form_invalid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        c = Collector()
        cleaned_datas = [form.cleaned_data for form in formset if form.is_valid()]
        if cleaned_datas:
            save_collect(*cleaned_datas, test=settings.TEST)
        return super(CollectBatchFormView, self).form_invalid(form)




def test(request):
    save_collect(*formdatas, test=True)
    return HttpResponseRedirect('/')


def generate_form_initial(request):
    if request.is_ajax():
        data = request.GET
        if request.method == "GET":
            contents = set_form_initial(**guess_time_range(request))
            return HttpResponse(contents, content_type="application/json")

class GenerateFormInitial(FormView):
    form_class = CollectForm
    success_url = '.'
    template_name = 'collect/collect_form.html'

    def get_context_data(self, **kwargs):
        context = super(GenerateFormInitial, self).get_context_data(**kwargs)
        context['formset'] = CollectFormset(initial)
        return context












