from django.shortcuts import render, redirect
from django.views.generic import CreateView, UpdateView, FormView, TemplateView

from .core import Collect
from .forms import CollectCreateForm

class CollectCreateView(FormView):
    template_name = 'collect/collect_form.html'
    form_class = CollectCreateForm
    success_url = '.'

    def form_valid(self, form):
        c = Collect()
        obj = c.create_collect(**form.cleaned_data)
        c.set_context(obj, test=False)
        c.save(obj)
        return super(CollectCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CollectCreateView, self).get_context_data(**kwargs)
        c = Collect()
        form_data = c.get_form(self.request, auto_on_staturday=True, translate=False)
        if form_data:
            context['form'] = CollectCreateForm(form_data)
        context['object_list'] = c.get_list()
        return context

def collect_detail(request, slug):
    c = Collect()
    object = c.get_object(slug)
    object_list = c.get_list()
    return render(request, 'collect/collect_detail.html', {'object': object, 'object_list':object_list})

def collect_delete(request, slug):
    # if request.method == "POST":
    c = Collect()
    c.delete(slug)
    return redirect('collect:create')

