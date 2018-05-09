from brian2 import *

def spike_plot(spike_mon):
  spike_plot_x = []
  spike_plot_y = []
  trains = spike_mon.spike_trains()
  for i in trains:
    spike_plot_x.extend(trains[i])

    sz = len(trains[i])
    vals = [i] * sz
    spike_plot_y.extend( vals )
  
  return spike_plot_x, spike_plot_y

taum = 10*ms
taupre = 20*ms
taupost = 20*ms

Ee = 0*mV
vt = -54*mV
vr = -60*mV
El = -74*mV
taue = 5*ms

F = 15*Hz
gmax = .01

dApre = .01
dApost = -dApre * (taupre / taupost) * 1.05
dApost *= gmax
dApre *= gmax

eqs_neurons = '''
dv/dt = (ge * (Ee-vr) + El - v) / taum : volt
dge/dt = -ge / taue : 1
'''

input = PoissonGroup(1000, rates=F)
neurons = NeuronGroup(100, eqs_neurons, threshold='v>vt', reset='v = vr', method='exact')
output = NeuronGroup(10, eqs_neurons, threshold='v>vt', reset='v = vr', method='exact')

###########################

S0 = Synapses(input, neurons,
             '''w : 1
                dApre/dt = -Apre / taupre : 1 (event-driven)
                dApost/dt = -Apost / taupost : 1 (event-driven)''',
             on_pre='''
                    ge += w
                    Apre += dApre
                    w = clip(w + Apost, 0, gmax)''',
             on_post='''
                    ge -= w
                    Apost += dApost
                    w = clip(w + dApre, 0, gmax)''',
             )
S0.connect()
S0.w = 'rand() * gmax'

# pretty sure [0,1] is the range of the weight to record.
# mon = StateMonitor(S0, 'w', record=[0, 1])
# NOOO [0,1] was actually record index 0 and 1...
# so we were just looking at indexes 0 and 1.

mon0 = StateMonitor(S0, 'w', record=range(100))
spike_mon0 = SpikeMonitor(neurons)

###########################

S1 = Synapses(neurons, output,
             '''w : 1
                dApre/dt = -Apre / taupre : 1 (event-driven)
                dApost/dt = -Apost / taupost : 1 (event-driven)''',
             on_pre='''
                    ge += w
                    Apre += dApre
                    w = clip(w + Apost, 0, gmax)''',
             on_post='''
                    ge -= w
                    Apost += dApost
                    w = clip(w + dApre, 0, gmax)''',
             )
S1.connect()
S1.w = 'rand() * gmax'

# pretty sure [0,1] is the range of the weight to record.
# mon = StateMonitor(S0, 'w', record=[0, 1])
# NOOO [0,1] was actually record index 0 and 1...
# so we were just looking at indexes 0 and 1.

mon1 = StateMonitor(S1, 'w', record=range(10))
spike_mon1 = SpikeMonitor(output)

###########################

run(2*second, report='text')

spike_plot_x0, spike_plot_y0 = spike_plot(spike_mon0)
spike_plot_x1, spike_plot_y1 = spike_plot(spike_mon1)

'''
print len(mon.w)
print len(mon.w[0])
print np.average(mon.w[0])
print np.average(mon.w[1])
print len(mon.w.T)
'''

# so we think that its # seconds * 1000 (ms granularity)
# but we dont know whats actualy inside there.

subplot(411)
plot(mon0.t/second, mon0.w.T/gmax)
xlabel('Time (s)')
ylabel('Weight / gmax')

subplot(412)
plot(spike_plot_x0, spike_plot_y0, '.k')

subplot(413)
plot(mon1.t/second, mon1.w.T/gmax)
xlabel('Time (s)')
ylabel('Weight / gmax')

subplot(414)
plot(spike_plot_x1, spike_plot_y1, '.k')

tight_layout()
show()




