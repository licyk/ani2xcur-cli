from ani2xcur.win2xcur import scale

def patch_win2xcur() -> None:
    """将补丁应用到 win2xcur 中"""
    try:
        import win2xcur.scale
    except ImportError:
        import win2xcur
        win2xcur.scale = scale
