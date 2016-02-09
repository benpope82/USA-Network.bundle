SHOWS_URL = 'http://tve-atcnbce.nbcuni.com/live/3/usa/containers/iPad'
EPISODES_URL = 'http://tve-atcnbce.nbcuni.com/live/3/usa/containers/%s/iPad?filterBy=episode'

####################################################################################################
def Start():

	ObjectContainer.title1 = 'USA Network'
	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'BRNetworking/2.7.0.1449 (iPad;iPhone OS-8.1)'

####################################################################################################
@handler('/video/usanetwork', 'USA Network')
@route('/video/usanetwork/shows')
def Shows():

	oc = ObjectContainer()

	if not Client.Platform in ('Android', 'iOS', 'Roku', 'Safari', 'tvOS', 'Konvergo', 'Mystery 4'):

		oc.header = 'Not supported'
		oc.message = 'This channel is not supported on %s' % (Client.Platform if Client.Platform is not None else 'this client')
		return oc

	for show in JSON.ObjectFromURL(SHOWS_URL):

		show_id = show['assetID']
		title = show['title']
		summary = show['description']
		try: thumb = show['images'][0]['images']['show_tile']
		except: thumb = ''

		oc.add(DirectoryObject(
			key = Callback(Episodes, show_id=show_id, show=title),
			title = title,
			summary = summary,
			thumb = Resource.ContentsOfURLWithFallback(thumb)
		))

	oc.objects.sort(key = lambda obj: obj.title)
	return oc

####################################################################################################
@route('/video/usanetwork/episodes/{show_id}')
def Episodes(show_id, show):

	oc = ObjectContainer(title2=show)

	for episode in JSON.ObjectFromURL(EPISODES_URL % show_id)['results']:

		if episode['type'] != 'video' or episode['subtype'] != 'episode' or episode['requiresAuth']:
			continue

		url = 'http://www.usanetwork.com/#%s|%s' % (show_id, episode['assetID'])

		oc.add(EpisodeObject(
			url = url,
			show = show,
			title = episode['title'],
			summary = episode['description'],
			thumb = Resource.ContentsOfURLWithFallback(episode['images'][0]['images']['episode_banner']),
			season = int(episode['seasonNumber']),
			index = int(episode['episodeNumber']) if 'episodeNumber' in episode else None,
			duration = episode['totalDuration'],
			originally_available_at = Datetime.FromTimestamp(episode['firstAiredDate'])
		))

	if len(oc) < 1:
		return ObjectContainer(header='Empty', message='There are no episodes available for this show')

	return oc
