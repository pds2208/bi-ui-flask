from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

from appconfig import Config

es = Elasticsearch(Config.ELASTICSEARCH_URL)


def search_postcode(search_string, filters, page_no):
    return search_field(search_string, filters, 'PostCode', page_no)


def search_name(search_string, filters, page_no):
    return search_field(search_string, filters, 'BusinessName', page_no)


def search_all(search_string, filters, page_no):
    return search_field(search_string, filters, 'ALL', page_no)


def search_field(search_string, filters, field, page_no):
    start = page_no * Config.ITEMS_PER_PAGE - Config.ITEMS_PER_PAGE

    orig_search_string = search_string
    search_string = check_reserved_characters(search_string)

    if field == 'ALL':
        s = Search(using=es, index=Config.INDEX) \
            .query("query_string", query=search_string)
    else:
        s = Search(using=es, index=Config.INDEX) \
            .query("simple_query_string", query=search_string, fields=[field])

    s = s[start:page_no * Config.ITEMS_PER_PAGE]

    employment_toggle = filters.get('employment-toggle', None)
    if employment_toggle:
        s = s.filter('terms', EmploymentBands=populate_filter(employment_toggle))

    turnover_toggle = filters.get('turnover-toggle', None)
    if turnover_toggle:
        s = s.filter('terms', Turnover=populate_filter(turnover_toggle))

    trading_toggle = filters.get('trading-toggle', None)
    if trading_toggle:
        s = s.filter('terms', TradingStatus=populate_filter(trading_toggle))

    legal_toggle = filters.get('legal-toggle', None)
    if legal_toggle:
        legal_map = {'Company': '1', 'Sole Proprietor': 2, 'Partnership': 3,'Public Corporation': 4,
                     'Central Government': 5, 'Local Authority': 6,
                     'Non-Profit Organisation': 7, 'Charity': 8}
        for n, i in enumerate(legal_toggle):
            legal_toggle[n] = str(legal_map.get(i))

        s = s.filter('terms', LegalStatus=populate_filter(legal_toggle))

    print(s.to_dict())

    res = s.execute()

    res['hits']['items_found'] = res['hits']['total']

    if res['hits']['total'] > Config.MAX_ITEMS_RETURNED:
        res['hits']['total'] = Config.MAX_ITEMS_RETURNED

    if res['hits']['total'] > Config.ITEMS_PER_PAGE:
        res['hits']['paging_active'] = True
    else:
        res['hits']['paging_active'] = False

    res['hits']['search_string'] = orig_search_string

    return res['hits']


def populate_filter(toggle):
    # We take the first character of the description (the value of the item in the filter).
    # This works for everything except legal status
    # where we have to do a substitution as seen above
    a = []
    for v in toggle[:-1]:
        a.append(v[0])
    a.append(toggle[-1][0])
    return a


def check_reserved_characters(string):
    # check for and escape
    reserved = ['"', '\', ' + ', "'""]
    for tag in reserved:
        string = string.replace(tag, '\\' + tag)
    return string
