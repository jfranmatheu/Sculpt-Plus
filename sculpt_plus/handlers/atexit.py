import atexit


first_time = True


@atexit.register
def on_quit():
    global first_time
    if not first_time:
        return
    print("[Sculpt+] atexit::on_quit()")
    first_time = False
    # from sculpt_plus.globals import G
    # G.hm_data.save()
