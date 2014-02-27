
from inspect import getfullargspec
from officelib.nsdbg import *  # @UnusedWildImport

globaldict = {
                'trace_spacer' : trace_spacer,
              'trace_scope' : trace_scope}
              
                         
def pfc(func):
    spec = getfullargspec(func)
    args, varargs, varkw, defaults, kwonlyarg, kwdefs, _annotations = spec

    annotation = "function: <%s.%s>" % (func.__module__, func.__name__)

    args = args or []
    varargs = varargs or ''
    varkw = varkw or {}
    defaults = defaults or []
    kwdefs = kwdefs or {}
    nargs = len(args) - len(defaults)
    print(kwdefs)
    print(kwonlyarg)
    nkwonlydefs = len(kwonlyarg) - len(kwdefs) 
    argsstr = ', '.join(args[:nargs]) + (', ' if nargs else '')
    
    default_str = ', '.join("%s=defaults[%d]" % (arg, val) 
                            for val, arg in enumerate(args[nargs:])) + (', ' if defaults else '')
    
    vararg_str = '*%s, ' % varargs if varargs else ''
    
    kwonlyarg_str = ', '.join(kwonlyarg[:nkwonlydefs]) + (', ' if nkwonlydefs else '') 
    
    kwdef_str = ', '.join("%s=kwdefs['%s']" % (k,k) for k in kwdefs.keys()) + (', ' if kwdefs else '')
    
    varkw_str = '**%s' % varkw if varkw else ''
    
    func_arg_str = ''.join((
                     '(',
                    argsstr,
                    default_str,
                    vararg_str,
                    kwonlyarg_str,
                    kwdef_str,
                    varkw_str,
                    ')'
                    )) 
                    
    if func_arg_str.endswith(', )'):
        func_arg_str = func_arg_str.replace(', )', ')')
    print(func_arg_str)
    
    call_arg_str = ''.join((
                            '(',
                            argsstr,
                            ', '.join(args[nargs:]) + ', ' if defaults else '', 
                            vararg_str,
#                             ', '.join("%s=%s" % (k,k) for k in kwdefs.keys()),
                            ', '.join("%s=%s" % (k,k) for k in kwonlyarg) + (', ' if kwonlyarg else ''),
                            varkw_str,
                            ')'    
                            ))
    print("Call arg str:", call_arg_str)
    func_def = 'def dynamicPFCwrapper%s:\n' % func_arg_str
    func_call = '    _return = func%s' % call_arg_str
    func_body = func_def + r'''
    global trace_scope
    global trace_spacer
    tss = '\n' + trace_spacer * trace_scope
    
    TFC_echo_write_dbg(''.join((
                                tss,
                                "Call to ",
                                annotation
                                ))
                   )
    
    trace_scope = trace_scope + 1
    
    try:
        t_call = tc()
    ''' + \
        func_call + '''
    finally: #print regardless of raised exception
        t_return = tc()
        trace_scope = trace_scope - 1
    
        TFC_echo_write_dbg(''.join((
                                      tss,
                                      "Return from ",
                                      annotation,
                                      tss,
                                      '   return time: %f seconds' % (t_return-t_call)
                                  ))
                           )
    
    return _return''' 
    
    namespace = {
                 'trace_scope' : trace_scope,
                 'trace_spacer' : trace_spacer,
                 'TFC_echo_write_dbg' : TFC_echo_write_dbg,
                 'tc' : perf_counter,
                 'annotation' : annotation,
                 'kwdefs' : kwdefs,
                 'defaults' : defaults,
                }
    
    namespace.update(globaldict)
    exec(func_body, locals(), locals())
    
    wrapper = locals()['dynamicPFCwrapper']

    return wrapper

@pfc
def func(pos1, pos2, default1=5, default2='defval2', *varargs, kwonly1, kwdef1='kwdefarg1', kwedf2='kwdef2', **kwargs):
    if default1:
        return func(1, 2, default1-1, kwonly1=2)
    return None
def func2():
    pass

func(1, 2, kwonly1 = 2, kwdef1 = 'Foo', kwdef2 = 'Bar')
