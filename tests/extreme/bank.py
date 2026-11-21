import math

def value_bank():
    out = {}
    out["none"] = None
    out["empty"] = ""
    out["spaces"] = "  "
    out["bool_t"] = True
    out["bool_f"] = False
    out["zero"] = 0
    out["neg0"] = -0.0
    out["nan"] = float("nan")
    out["inf"] = float("inf")
    out["ninf"] = float("-inf")
    out["max"] = 1.7976931348623157e308
    out["2p53"] = 2**53
    out["huge"] = 1e15
    out["str30"] = "30"
    out["p30"] = "+30"
    out["str3e1"] = "3e1"
    out["comma30"] = "30,5"
    out["unit30"] = "30 m"
    out["hex1E"] = "0x1E"
    out["under1k"] = "1_000"
    out["arabic"] = "٣٠"
    out["zerowidth"] = "\u200b30"
    out["neg"] = -5.0
    out["text"] = "some text"
    out["long10k"] = "x" * 10_000
    return out

def enum_bank():
    return ["Highway", "OPTIMIZED", " high way ", "Other option", "single side",
            "Both Sides", "None", "No", "Yes", "high", "highway bridge"]
