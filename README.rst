denonavr_serial: python library for Denon AVR Receivers
=======================================================

Supported Receivers
-------------------

Tested:

* AVR-3805

Untested, but likely supported:

* AVC-3890


Adding a support for a different receiver
-----------------------------------------

Patches adding support for other Denon receivers are welcome. It looks like many use a similar protocol for control, with the notable differences being:

* Which sources are supported for a particular model
* The number/names of non-main zones
* The volume scale

This information can be found on Denon's website, for RS-232 control.
