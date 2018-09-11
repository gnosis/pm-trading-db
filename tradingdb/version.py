__version__ = '1.7.3'
__version_info__ = tuple([int(num) if num.isdigit() else num for num in __version__.replace('-', '.', 1).split('.')])

try:
    import git
    git_repo = git.Repo(search_parent_directories=True)
    try:
        __git_branch__ = str(git_repo.active_branch)
    except Exception:
        __git_branch__ = ''
    __git_author__ = str(git_repo.head.commit.author)
    __git_message__ = git_repo.head.commit.message.strip()
    __git_head_hash__ = git_repo.head.object.hexsha
    __git_commit_datetime__ = str(git_repo.head.commit.committed_datetime)
    __git_info__ = {
        'author': __git_author__,
        'branch': __git_branch__,
        'datetime': __git_commit_datetime__,
        'head': __git_head_hash__,
        'message': __git_message__,
    }
except ImportError:
    __git_info__ = {'error': 'Git not installed'}
except git.exc.InvalidGitRepositoryError:
    __git_info__ = {'error': 'Git repository not found'}
