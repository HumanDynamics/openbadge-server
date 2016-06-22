from matplotlib import pyplot, dates, rcParams
from django.conf import settings

import os, csv

def groupStatGraph(durations, num_meetings, days, names, graph_path):
	
	total = len(durations)
	group_numbers = [name.split()[-1] for name in names]
	
	rcParams['figure.figsize'] = 10, total+10
	
	for i in xrange(total):
		ax = pyplot.subplot(total, 1, i+1)
		pyplot.plot(days, durations[i], linestyle='-', linewidth=2.0, marker='D', markersize=2.0, label='duration')
		pyplot.bar(days, num_meetings[i], facecolor='#ff3687', edgecolor='white', label='meetings', align='center')
		pyplot.ylim(0, 10.3)
		
		if i!= total-1:
			pyplot.setp(ax.get_xticklabels(), visible=False)
		if i == 0:
			pyplot.legend(loc='upper left', frameon=False)
		pyplot.ylabel(group_numbers[i], rotation=0)
		
		for x,y in zip(days, durations[i]):
			pyplot.text(x, y+0.05, '%.1f' % y, ha='center', va= 'bottom', fontsize=9.0)

	
	pyplot.xticks(rotation=90)
	pyplot.tight_layout()
	pyplot.subplots_adjust(hspace=0.05)
	
	ax = pyplot.gca()
	ax.xaxis.set_major_locator(dates.DayLocator(bymonthday=range(1,32), interval=1))
	ax.xaxis.set_major_formatter(dates.DateFormatter('%a-%b-%d'))
	
	pyplot.savefig(graph_path + '/team_meeting_summary_graph.png')
	pyplot.close()
	
	agg_duration = [sum(duration) for duration in zip(*durations)]
	agg_num_meetings = [sum(num) for num in zip(*num_meetings)]
	
	total_time = sum(agg_duration)
	
	agg_graph_file = aggregateGraph(agg_duration, agg_num_meetings, days, graph_path)
	
	csv_file = generateTable(durations, days, names, graph_path)
	
	return {'group_img':'team_meeting_summary_graph.png', 'agg_img':agg_graph_file,
		'time':{'hrs':int(total_time), 'mins': int((total_time-int(total_time))*60)},
		'num_meetings':sum(agg_num_meetings), 'stats_csv':csv_file}
	
def aggregateGraph(durations, num_meetings, days, graph_path):
		
	rcParams['figure.figsize'] = 8, 5.5
	
	pyplot.plot(days, durations, linestyle='-', linewidth=2.0, marker='D', markersize=2.0, label='duration')
	pyplot.bar(days, num_meetings, facecolor='#ff3687', edgecolor='white', label='meetings', align='center')
	
	pyplot.xticks(rotation=90)
	pyplot.tight_layout()
	
	ax = pyplot.gca()
	ax.xaxis.set_major_locator(dates.DayLocator(bymonthday=range(1,32), interval=1))
	ax.xaxis.set_major_formatter(dates.DateFormatter('%a-%b-%d'))
	
	pyplot.legend(loc='upper left', frameon=False)
		
	pyplot.savefig(graph_path + '/aggregate_summary_graph.png')
	pyplot.close()
	
	return 'aggregate_summary_graph.png'
	
def generateTable(durations, days, names, table_path):
	
	headers = days
	headers.insert(0, 'Group\Date')
	
	csv_data = durations
	
	for i in xrange(len(names)):
		csv_data[i].insert(0, names[i])
		
	csv_data.insert(0, headers)
	
	table_stats = csv.writer(open(table_path + '/group_stats.csv', 'wb'))
	table_stats.writerows(csv_data)
	
	return 'group_stats.csv'
