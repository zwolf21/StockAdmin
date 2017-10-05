from pprint import pprint

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import CreateView, UpdateView, FormView, TemplateView, ListView, DetailView, DeleteView, View
from django.conf import settings

from .forms import CollectForm, CollectFormset, ConfigForm, CollectMergeForm, FORMSET_INITIAL
from .models import Collector, save_collect, set_form_initial, guess_time_range, merge_collect


# 집계 항목 보기
class CollectDetailView(DetailView):
    template_name = 'collect/collect_detail.html'

    def get_object(self):
        c = Collector()
        return c.get_object(self.kwargs.get('slug'))

    def get_context_data(self, **kwargs):
        kind = self.kwargs.get('kind')
        c = Collector()
        context = super(CollectDetailView, self).get_context_data(**kwargs)
        context['object_list'] = c.get_queryset() # 집계 리스트
        context['config'] = c.get_config(kinds=[kind]) # 집계시 설정정보
        context['objects'] = c.get_parsed(self.get_object().get('slug')) # 집계 양식 컨텍스트
        return context


# 집계 생성하기
class CollectFormView(FormView):
    template_name = 'collect/collect_form.html'
    form_class = CollectForm

    def get_success_url(self):
        c = Collector()
        return reverse_lazy('collect:detail', args=(c.last()['slug'], ))

    def form_valid(self, form):
        obj = save_collect(form.cleaned_data, test=settings.TEST)
        # self.success_url = reverse('collect:detail', args=(obj['slug'],))
        return super(CollectFormView, self).form_valid(form)
    
    # 집계 내역 합치는 POST 받기
    def form_invalid(self, form):
        print(form.data)
            # c = Collector()
            # slugs = self.request.POST.get('slugs')
            # if slugs:
            #     print('slugs:', slugs)
            #     # c.merge_collect(*slugs)
        return super(CollectFormView, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(CollectFormView, self).get_context_data(**kwargs)
        Form = self.get_form_class()
        context['form'] = Form(kinds=[self.kwargs.get('kind')])
        c = Collector()
        context['object_list'] = c.get_queryset()
        return context


class CollectMergeFormView(FormView):
    template_name = 'collect/collect_merge_form.html'
    form_class = CollectMergeForm

    def get_success_url(self):
        c = Collector()
        return reverse_lazy('collect:detail', args=(c.last()['slug'], ))

    def form_valid(self, form):
        # pprint(form.cleaned_data)
        if merge_collect(**form.cleaned_data):
            return super(CollectMergeFormView, self).form_valid(form)
        return HttpResponseRedirect('.')

    def get_context_data(self, **kwargs):
        context = super(CollectMergeFormView, self).get_context_data(**kwargs)
        c = Collector()
        context['object_list'] = c.get_queryset()
        return context



# 집계 항목 지정 삭제
class CollectDeleteView(DeleteView):

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

# 집계 리스트 전부 삭제
def clear(request):
    if request.method == "POST":
        c = Collector()
        c.clear()
    return HttpResponseRedirect(reverse('collect:create', args=('LABEL', )))

# 일괄 집계 생성
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






# 설정 뷰
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
        context['form'] = Form(initial=c.config.get(kind))
        context['object_list'] = c.get_queryset()
        return context

# 구분에 따른 자동 폼 데이터 전송해 주기
def generate_form_initial(request):
    if request.is_ajax():
        if request.method == "GET":
            contents = set_form_initial(**guess_time_range(request))
            return HttpResponse(contents, content_type="application/json")












