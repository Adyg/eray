from django.core.paginator import Paginator

class ErayPaginator(Paginator):
    """Custom paginator, will only display a subset of all available pages
    """

    def __init__(self, *args, **kwargs):
        """
        :param page_count: Number of pages that will be visible on either side of the current page
        """
        self.page_count = kwargs.pop('page_count', 3)

        super(ErayPaginator, self).__init__(*args, **kwargs)

    def _get_page(self, *args, **kwargs):
        self.page = super(ErayPaginator, self)._get_page(*args, **kwargs)

        return self.page

    @property
    def page_range(self):

        return range(max(self.page.number - self.page_count, 1),
                     min(self.page.number + self.page_count + 1, self.num_pages + 1))