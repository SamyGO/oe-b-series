import oe.maketype
import bb.msg

def typed_value(key, d):
    """Construct a value for the specified metadata variable, using its flags
    to determine the type and parameters for construction."""
    var_type = d.getVarFlag(key, 'type')
    flags = d.getVarFlags(key)

    try:
        return oe.maketype.create(d.getVar(key, True) or '', var_type, **flags)
    except (TypeError, ValueError), exc:
        bb.msg.fatal(bb.msg.domain.Data, "%s: %s" % (key, str(exc)))
