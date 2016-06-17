from matplotlib import pyplot, dates
from django.conf import settings

def overallGraph(durations, num_meetings, days, names):
	
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
		
	pyplot.savefig(settings.MEDIA_ROOT+'/tmp/team_meeting_summary_graph.png')
	pyplot.close()
	
	temp1 = [sum(duration) for duration in durations]
	temp2 = [sum(num) for num in num_meetings]
	
	return {'img':'team_meeting_summary_graph.png', 'time':sum(temp1), 'num_meetings':sum(temp2)}
		
		
