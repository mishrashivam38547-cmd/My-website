import argparse, sys, os, tkinter as tk
from tkinter import filedialog, messagebox
from . import core

def pause():
    try: input("\nEnter dabakar continue karein...")
    except (EOFError, KeyboardInterrupt): pass

def print_report(title, body, extra=None):
    print("\n" + "=" * 62 + "\n" + title + "\n" + "=" * 62)
    print(body)
    try:
        ans = input("\nIs result ki TXT + JSON report save karein? [Y/n]: ").strip().lower()
    except (EOFError, KeyboardInterrupt): ans = "n"
    if ans in ("", "y", "yes"):
        a, b = core.save_report(title, body, extra)
        print(f"Saved:\n  {a}\n  {b}")
    pause()

def terminal():
    while True:
        print("\n" + "=" * 44)
        print("🐉 RED DRAGON — Wi-Fi Security Toolkit")
        print("=" * 44)
        print("1. Nearby Wi-Fi scanner")
        print("2. Network diagnostics")
        print("3. Wi-Fi security checklist")
        print("4. Analyze PCAP / PCAPNG file")
        print("5. Adapter & capability check")
        print("6. Save environment report")
        print("7. Help / limitations")
        print("0. Exit")
        try: choice = input("\nOption: ").strip()
        except (EOFError, KeyboardInterrupt): print(); break
        if choice == "1":
            body, rows = core.wifi_scan(); print_report("Wi-Fi Scan", body, {"rows": rows})
        elif choice == "2":
            body = core.diagnostics(); print_report("Network Diagnostics", body)
        elif choice == "3":
            body = core.audit(); print_report("Security Audit Checklist", body)
        elif choice == "4":
            p = input("PCAP/PCAPNG file ka full path: ").strip().strip('"')
            body, details = core.analyze_capture(p); print_report("Capture Analysis", body, details)
        elif choice == "5":
            body = core.adapter_report(); print_report("Adapter Check", body)
        elif choice == "6":
            body = str(core.environment())
            a, b = core.save_report("Environment Report", body, core.environment())
            print(f"Saved:\n{a}\n{b}"); pause()
        elif choice == "7":
            print("\nNo root required. No monitor mode, injection, deauthentication, password cracking, or live packet capture.")
            print("Android scan support depends on Termux:API, permissions, and OS version.")
            print("Use only networks and capture files you own or are authorized to analyze."); pause()
        elif choice == "0": break
        else: print("Invalid option.")
    print("Red Dragon closed.")

def gui():
    root = tk.Tk()
    root.title("Red Dragon — Wi-Fi Security Toolkit")
    root.geometry("820x600")
    try: root.configure(bg="#111318")
    except Exception: pass
    title = tk.Label(root, text="🐉 RED DRAGON", font=("Arial", 20, "bold"), fg="#ff4040", bg="#111318")
    title.pack(pady=(12, 2))
    sub = tk.Label(root, text="Authorized, non-invasive Wi-Fi diagnostics", fg="#dddddd", bg="#111318")
    sub.pack(pady=(0, 10))
    output = tk.Text(root, wrap="word", font=("Consolas", 10), bg="#1b1e25", fg="#f2f2f2", insertbackground="white")
    output.pack(fill="both", expand=True, padx=12, pady=8)
    def show(name, body, extra=None):
        output.delete("1.0", "end"); output.insert("end", name + "\n" + "="*50 + "\n" + body)
        if messagebox.askyesno("Save report", "TXT + JSON report save karein?"):
            a,b = core.save_report(name, body, extra)
            messagebox.showinfo("Saved", f"{a}\n{b}")
    bar = tk.Frame(root, bg="#111318"); bar.pack(fill="x", padx=8, pady=8)
    actions = [
        ("Wi-Fi Scanner", lambda: (lambda x: show("Wi-Fi Scan", x[0], {"rows":x[1]}))(core.wifi_scan())),
        ("Diagnostics", lambda: show("Network Diagnostics", core.diagnostics())),
        ("Security Audit", lambda: show("Security Audit", core.audit())),
        ("Adapter Check", lambda: show("Adapter Check", core.adapter_report())),
        ("Analyze Capture", lambda: (lambda p: show("Capture Analysis", *core.analyze_capture(p)))(filedialog.askopenfilename(title="Choose PCAP/PCAPNG file"))),
    ]
    for label, fn in actions:
        tk.Button(bar, text=label, command=fn, bg="#292d36", fg="white", activebackground="#454b57").pack(side="left", padx=3, pady=3)
    output.insert("end", "Choose a feature above.\n\nLimitations: no monitor mode, injection, deauthentication, password cracking, or live packet capture.\n")
    root.mainloop()

def main():
    parser = argparse.ArgumentParser(description="Red Dragon Wi-Fi Security Toolkit")
    parser.add_argument("--gui", action="store_true", help="Launch Tkinter GUI (desktop Linux only)")
    args = parser.parse_args()
    if args.gui:
        try: gui()
        except Exception as e:
            print(f"GUI unavailable: {e}\nStarting terminal menu instead.")
            terminal()
    else: terminal()

if __name__ == "__main__": main()
