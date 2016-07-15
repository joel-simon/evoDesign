# import experiments
# print vars(experiments)
framework_name = 'height'
__import__('experiments', globals(), fromlist=[framework_name], level=1)
framework_module = getattr(backends, framework_name)
Framework = getattr(framework_module,
                    '%sFramework' % fwSettings.backend.capitalize())
print(Framework)
