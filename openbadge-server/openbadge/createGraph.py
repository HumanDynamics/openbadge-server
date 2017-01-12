from matplotlib import pyplot, dates, rcParams
import numpy, datetime
from django.conf import settings

def individualGraph(meetings, start, period):
	
	img_names = []
	agg_duration = [0.0]*period
	total_time = 0.0
	num_meetings = 0
	
	raw_date = [datetime.datetime.now() - datetime.timedelta(i) for i in xrange(period)]
	raw_date.reverse()
	days = dates.date2num(raw_date)
	
	rcParams.update({'figure.autolayout': True})
	
	for meeting in meetings:

		group = meeting.keys()[0]
		data = meeting[group]
		
		day_num = []
		day_time = []
		
		for i in xrange(period):
			current = data.filter(start_time__lte = start - datetime.timedelta(i), start_time__gt = start - datetime.timedelta(i+1))
			day_num.append(len(current))
			agg_duration[i] += len(current)
			times = [meeting.end_time - meeting.start_time for meeting in current]
			day_time.append((sum(times, datetime.timedelta()).total_seconds())/3600.0)
		
		total_time += sum(day_time)
		num_meetings += sum(day_num)
		
		day_num.reverse()
		day_time.reverse()
		
		day_num = numpy.array(day_num)
		day_time = numpy.array(day_time)
		
		pyplot.bar(days, day_num, facecolor='#9999ff', edgecolor='white', label='meetings')
		pyplot.bar(days, -day_time, facecolor='#ff9999', edgecolor='white', label='duration')
		
		for x,y in zip(days, day_num):
			if y > 0:
				pyplot.text(x+0.4, y+0.05, '%d' %y, ha='center', va='bottom')
			else:
				pyplot.text(x+0.4, y+0.05, '', ha='center', va='bottom')
			
		for x,y in zip(days, day_time):
			if y > 0.0:
				pyplot.text(x+0.4, -y-0.2, '%.2f' %y, ha='center', va='bottom')
			else:
				pyplot.text(x+0.4, -y-0.2, '', ha='center', va='bottom')
				
		#pyplot.xlabel('Day')
		#pyplot.ylabel('Number of Meetings/ Time (hrs)')
		pyplot.ylim(max(day_time)*-1.1, max(day_num)*1.1)
		
		ax = pyplot.gca()
		ax.spines['top'].set_color('none')
		ax.spines['right'].set_color('none')
		ax.xaxis.set_ticks_position('bottom')
		ax.yaxis.set_ticks_position('left')
		
		ax.set_yticklabels([str(abs(x)) for x in ax.get_yticks()])
		ax.spines['bottom'].set_position(('data',0))
		pyplot.xticks(rotation=90)
		
		ax.xaxis.set_major_locator(dates.DayLocator(bymonthday=range(1,32), interval=1))
		ax.xaxis.set_major_formatter(dates.DateFormatter('%a-%b-%d'))
		
		xticks = ax.xaxis.get_major_ticks()
		xticks[0].label1.set_visible(False)
		xticks[-1].label1.set_visible(False)
			
		ax.yaxis.grid()
		pyplot.legend(loc='upper left', frameon=False)
		
		pyplot.savefig(settings.MEDIA_ROOT+'/tmp/g'+group+'.png')
		pyplot.close()
		
		img_names.append(group)
		
		metadata = {}
		metadata['num_meetings'] = num_meetings
		metadata['days'] = days
		metadata['agg_duration'] = agg_duration
		metadata['time'] = total_time
		metadata['img'] = img_names
		
	return metadata
		
def aggregateGraph(duration, days):
	
	rcParams.update({'figure.autolayout': True})
	
	duration.reverse()
	
	pyplot.plot(days, duration, linewidth=1.0, linestyle='-', marker='D', label='meetings')
	ax = pyplot.gca()
	ax.spines['top'].set_color('none')
	ax.spines['right'].set_color('none')
	ax.xaxis.set_ticks_position('bottom')
	ax.yaxis.set_ticks_position('left')
	
	ax.xaxis.set_major_locator(dates.DayLocator(bymonthday=range(1,32), interval=1))
	ax.xaxis.set_major_formatter(dates.DateFormatter('%a-%b-%d'))
	
	pyplot.xticks(rotation=90)
	pyplot.ylim(min(duration)*1.1, max(duration)*1.1)
	
	#pyplot.xlabel('Days')
	pyplot.ylabel('Number of Meetings')
	
	ax.yaxis.grid()
	pyplot.legend(loc='upper left', frameon=False)
	
	pyplot.savefig(settings.MEDIA_ROOT+'/tmp/agg.png')
	pyplot.close()
