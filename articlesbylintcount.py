import toolforge
import pymysql
from botbase import *

conn = toolforge.connect('enwiki', cluster = 'analytics' )
query = '''
select page_title
, count(*) as page_count
, sum(case when linter_params like '%"name":"center"%' then 1 end) as tag_center
, sum(case when linter_params like '%"name":"small"%' then 1 end) as tag_small
, sum(case when linter_params like '%"name":"span"%' then 1 end) as tag_span
, sum(case when linter_params like '%"name":"div"%' then 1 end) as tag_div
, sum(case when linter_params like '%"name":"b"%' then 1 end) as tag_b
, sum(case when linter_params like '%"name":"i"%' then 1 end) as tag_i
, sum(case when linter_params like '%"name":"s"%' then 1 end) as tag_s
from linter
join page on page.page_id = linter.linter_page
where page.page_namespace=0 and linter_cat != 2
group by page.page_id
order by count(*) desc, page_title asc
limit 1000;
'''

tablerows = []
with conn.cursor(pymysql.cursors.DictCursor) as cur:
    cur.execute(query)
    data = cur.fetchall()
    for row in data:
        tablerows.append('\n|-\n| [[' + row['page_title'].decode().replace('_', ' ') + ']]\n|' + str(row['count(*)']))
    
    page = p.Page(site, 'User:Galobot/report/Articles_by_Lint_Errors')
    page.text = 'Generated by [[Quarry:query/31876|this query]]. Excludes [[Special:LintErrors/obsolete-tag|obsolete HTML tag lint errors]]. Updated on ~~~~~. \n{| class="wikitable sortable"\n!Page title\n!Lint errors' + "".join(tablerows) + "\n|}"
    page.savewithshutoff(summary = 'Update "Articles by Lint Errors" report', minor = False) #edit page

conn.close()
