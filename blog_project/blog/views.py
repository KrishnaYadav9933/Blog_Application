from django.shortcuts import render, get_object_or_404
from blog.models import Post
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.mail import send_mail
from blog.forms import EmailSendForm, CommentForm
from taggit.models import Tag

# Create your views here.
def post_list_view(request, tag_slug=None):
    post_list = Post.objects.all()
    tag=None
    if tag_slug:
        tag=get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tag__in=[tag])
    paginator=Paginator(post_list, 2)
    page_number = request.GET.get('page')
    try:
        post_list = paginator.page(page_number)
    except PageNotAnInteger:
        post_list = paginator.page(1)
    except EmptyPage:
        post_list=paginator.page(paginator.num_pages)

    return render(request, './blog/post_list.html', {'post_list':post_list, 'tag':tag})

def post_detail_view(request, year, month, day, slug2):
    post_object=get_object_or_404(Post, slug=slug2,
                           status='published',
                           publish__year=year,
                           publish__month=month,
                           publish__day=day,
                           )
    comments = post_object.comments.filter(active=True)
    csubmit = False
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit = False)
            new_comment.post = post_object
            new_comment.save()
            csubmit = True
    else:
        form = CommentForm()
    return render(request, 'blog/post_detail.html', {'post':post_object, 'form':form, 'csubmit':csubmit, 'comments':comments})


def mail_send_view(request, id):
    post=get_object_or_404(Post, id=id, status='published')
    sent = False
    if request.method=='POST':
        form=EmailSendForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            subject='{}({}) recommends you to read "{}"'.format(cd['name'],cd['email'],post.title)
            post_url=request.build_absolute_uri(post.get_absolute_url())
            message='Read Post At:\n {}\n\n{}\'s Comments:\n{}'.format(post_url, cd['name'],cd['comments'])
            send_mail(subject, message, 'krishna993344@gmail.com', [cd['to']])
            sent=True
    else:
        form=EmailSendForm()
    return render(request, 'blog/sharebyemail.html', {'form':form, 'post':post, 'sent':sent})