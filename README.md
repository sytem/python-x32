python-x32
==========

This fork of python-x32 library is a OSC proxy for X32. Proxy request changes from mixer (ip given from command line) and forwards them to N target-hosts (defined at the code). Each target have regex-filter to limit packets sent. For example using arduino ethernet as button panel, it might be good idea to filter fader values out. Also this proxy take care of sending /xremote-commands every 10 seconds to mixer, so clients such TouchOSC (http://hexler.net/software/touchosc) can be used with return data from mixer.

Second reason to use proxy is limit of 4 clients to one mixer. Using button-panels or/and touchOSC ipad-clients , it is easy to have lot more clients.

This proxy is not for behringer own software, because meter-data is not forwarded.



Behringer documentation for API: http://www.behringer.com/assets/X32_OSC_Remote_Protocol.pdf



