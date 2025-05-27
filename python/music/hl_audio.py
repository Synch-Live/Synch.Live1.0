# Calculate volume of audio sample based on psi value
# Param:
#         psi    - current psi value
#         start  - minimum psi value required to start
#				   increasing volume of audio sample 
def getVolumeForPsi(psi, start):
	end = start + 0.1
	range = end - start
	val = (psi - start) / range
	return min(1, max(0, val)) # clamp 0..1

# Play audio while game is running
def whileOn(channel, sampleIndex, val, prev):
	if channel.name == 'running':
		op('play').par.value0 = 1
	return
	
# Stop audio while game is not running
def whileOff(channel, sampleIndex, val, prev):
	if channel.name == 'running':
		op('play').par.value0 = 0
	return
	
# Restart tracks at start when starting game
def onOffToOn(channel, sampleIndex, val, prev):
	if channel.name == 'running':
		op('restart').par.value0.pulse()
	return
	
# Fade in and out audio based on current psi value
# this function will be triggered every time of the
# source channels changes
def onValueChange(channel, sampleIndex, val, prev):
	# Set main volume of all samples to 0 if not running
	# otherwise max volume
	if channel.name == 'running':
		op('main_vol').par.gain = val
		
	if channel.name == 'psi':
		psi = val
		
		# Calculate current volume levels for each sound
		a_level = getVolumeForPsi(psi, 0.3)
		b_level = getVolumeForPsi(psi, 0.5)
		c_level = getVolumeForPsi(psi, 0.75)
		d_level = getVolumeForPsi(psi, 0.9)
		
		if psi >= 1:
			d_level = 1
			
		
		# Set volume levels of sound samples
		op('A_level').par.gain = a_level
		op('B_level').par.gain = b_level
		op('C_level').par.gain = c_level
		op('D_level').par.gain = d_level

		
	return
	