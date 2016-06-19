from matplotlib import pyplot, dates
from django.conf import settings

import os

def groupStatGraph(durations, num_meetings, days, names, graph_path):
	
	total = len(durations)
	
	for i in xrange(total):
		ax = pyplot.subplot(total, 1, i+1)
		pyplot.plot(days, durations[i], linestyle='-', linewidth=2.0, marker='D', markersize=2.0, label='duration')
		pyplot.bar(days, num_meetings[i], facecolor='#ff3687', edgecolor='white', label='meetings', align='center')
		pyplot.ylim(0, 10.3)
		if i!= total-1:
			pyplot.setp(ax.get_xticklabels(), visible=False)
		if i == 0:
			pyplot.legend(loc='upper left', frameon=False)
		pyplot.ylabel(names[i])
	
	pyplot.xticks(rotation=90)
	pyplot.tight_layout()
	pyplot.subplots_adjust(hspace=0.02)
	
	ax = pyplot.gca()
	ax.xaxis.set_major_locator(dates.DayLocator(bymonthday=range(1,32), interval=1))
	ax.xaxis.set_major_formatter(dates.DateFormatter('%a-%b-%d'))
	
	pyplot.savefig(graph_path + '/team_meeting_summary_graph.png')
	pyplot.close()
	
	agg_duration = [sum(duration) for duration in zip(*durations)]
	agg_num_meetings = [sum(num) for num in zip(*num_meetings)]
	
	total_time = sum(agg_duration)
	
	agg_graph_file = aggregateGraph(agg_duration, agg_num_meetings, days, graph_path)
	
	return {'group_img':'team_meeting_summary_graph.png', 'agg_img':agg_graph_file,
		'time':{'hrs':int(total_time), 'mins': int((total_time-int(total_time))*60)}, 'num_meetings':sum(agg_num_meetings)}
	
def aggregateGraph(durations, num_meetings, days, graph_path):
		
	pyplot.plot(days, durations, linestyle='-', linewidth=2.0, marker='D', markersize=2.0, label='duration')
	pyplot.bar(days, num_meetings, facecolor='#ff3687', edgecolor='white', label='meetings', align='center')
	
	pyplot.xticks(rotation=90)
	pyplot.tight_layout()
	
	ax = pyplot.gca()
	ax.xaxis.set_major_locator(dates.DayLocator(bymonthday=range(1,32), interval=1))
	ax.xaxis.set_major_formatter(dates.DateFormatter('%a-%b-%d'))
		
	pyplot.savefig(graph_path + '/aggregate_summary_graph.png')
	pyplot.close()
	
	return 'aggregate_summary_graph.png'
		
