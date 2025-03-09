import win32com.client
def name_model(item):
    stk = win32com.client.Dispatch("STK11.Application")
    root = stk.Personality2
    satellite = root.CurrentScenario.Children.Item("Tianhe")
    mcs = satellite.Propagator.MainSequence
    comp = mcs.Item(item)
    return comp.name


