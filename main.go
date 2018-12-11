package main

import (
	"bytes"
	"flag"
	"fmt"
	"log"
	"os"
	"os/exec"
	"sort"
	"strconv"
	"strings"
	"time"

	"github.com/cghdev/gotunl"
	aw "github.com/deanishe/awgo"
	"github.com/tidwall/gjson"
)

var (
	iconConnected    = &aw.Icon{Value: "icons/locked.png"}
	iconDisconnected = &aw.Icon{Value: "icons/unlocked.png"}
	iconConnecting   = &aw.Icon{Value: "icons/unlocked2.png"}
	iconIssue        = &aw.Icon{Value: "icons/issue.png"}
	iconDisconnect   = &aw.Icon{Value: "/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/ToolbarDeleteIcon.icns"}
)
var version = "1.0.0"
var wf *aw.Workflow

type connections struct {
	status     string
	clientAddr string
	serverAddr string
	timestamp  int64
	id         string
	name       string
}

func listConnections(gt *gotunl.Gotunl, search string) []connections { // add output format as json?
	cons := gt.GetConnections()
	c := []connections{}
	ptmp := connections{}
	for pid, p := range gt.Profiles {
		ptmp.status = "Disconnected"
		if strings.Contains(cons, pid) {
			ptmp.status = strings.Title(gjson.Get(cons, pid+".status").String())
			ptmp.serverAddr = gjson.Get(cons, pid+".server_addr").String()
			ptmp.clientAddr = gjson.Get(cons, pid+".client_addr").String()
			ptmp.timestamp = gjson.Get(cons, pid+".timestamp").Int()
		}
		name := gjson.Get(p.Conf, "name").String()
		if search == "" || strings.Contains(strings.ToLower(name), strings.ToLower(search)) {
			ptmp.id = strconv.Itoa(p.ID)
			ptmp.name = name
			c = append(c, ptmp)
		}
		if ptmp.status == "Connecting" {
			wf.Rerun(3)
		}
	}
	sort.Slice(c, func(i, j int) bool {
		return c[i].id < c[j].id
	})
	sort.Slice(c, func(i, j int) bool {
		return c[i].status != "Disconnected"
	})
	return c
}

func disconnect(gt *gotunl.Gotunl, id string) {
	if id == "all" {
		gt.StopConnections()
	} else {
		for pid, p := range gt.Profiles {
			if id == gjson.Get(p.Conf, "name").String() || id == strconv.Itoa(p.ID) {
				gt.DisconnectProfile(pid)
			}
		}
	}

}

func connect(gt *gotunl.Gotunl, id string) {
	for pid, p := range gt.Profiles {
		name := gjson.Get(p.Conf, "name").String()
		if id == name || id == strconv.Itoa(p.ID) {
			_, auth := gt.GetProfile(pid)
			user := ""
			password := ""
			if auth != "" {
				if auth[len(auth)-3:] == "pin" {
					var otp string
					user = "pritunl"
					pass := popup("Enter the PIN: ", true)
					if auth == "otp_pin" {
						otp = popup("Enter the OTP code: ", false)
					}
					password = string(pass) + otp
				}
				if user == "" {
					user = popup("Enter the username: ", false)
				}
				if password == "" {
					password = popup("Enter the password: ", true)
				}
			}
			gt.ConnectProfile(pid, user, password)
		}
	}
}

func runOsa(command string) bytes.Buffer {
	var out bytes.Buffer
	cmd := exec.Command("osascript")
	cmd.Stdin = bytes.NewBuffer([]byte(command))
	cmd.Stdout = &out
	err := cmd.Run()
	if err != nil {
		log.Fatal("There as an error: " + err.Error())
	}
	return out
}
func popup(msg string, pwd bool) string {
	var out bytes.Buffer
	hidden := ""
	if pwd {
		hidden = "with hidden answer"
	}
	command := fmt.Sprintf(`Tell application "System Events" to display dialog "%v" default answer "" %v`, msg, hidden)
	out = runOsa(command)
	res := strings.Split(out.String(), ":")[2]

	return strings.Trim(res, "\n")
}

func formatSince(t time.Time) string {
	Day := 24 * time.Hour
	ts := time.Since(t)
	sign := time.Duration(1)
	var days, hours, minutes, seconds string
	if ts < 0 {
		sign = -1
		ts = -ts
	}
	d := sign * (ts / Day)
	ts = ts % Day
	h := ts / time.Hour
	ts = ts % time.Hour
	m := ts / time.Minute
	ts = ts % time.Minute
	s := ts / time.Second
	if d > 0 {
		days = fmt.Sprintf("%d days ", d)
	}
	if h > 0 {
		hours = fmt.Sprintf("%d hrs ", h)
	}
	if m > 0 {
		minutes = fmt.Sprintf("%d mins ", m)
	}
	seconds = fmt.Sprintf("%d secs", s)
	return fmt.Sprintf("%v%v%v%v", days, hours, minutes, seconds)
}
func run() {
	gt := *gotunl.New()
	l := flag.Bool("l", false, "List connections")
	c := flag.String("c", "", "Connect to profile ID or Name")
	d := flag.String("d", "", "Disconnect profile or \"all\"")
	s := flag.String("s", "", "Search for profile")

	flag.Parse()
	if len(os.Args) < 2 {
		flag.Usage()
		os.Exit(1)
	}
	if *l {
		conns := listConnections(&gt, *s)
		ic := &aw.Icon{}
		action := ""
		sub := ""
		submod := ""
		for _, co := range conns {
			switch co.status {
			case "Connected":
				ic = iconConnected
				action = "-d " + co.id
				sub = "↩ to disconnect, ⌘ for details"
				ts := time.Unix(co.timestamp, 0)
				since := formatSince(ts)
				submod = "Server: " + co.serverAddr + " | Client: " + co.clientAddr + " | " + since
			case "Disconnected":
				ic = iconDisconnected
				action = "-c " + co.id
				sub = "↩ to connect"
			case "Connecting":
				ic = iconConnecting
				action = "-d " + co.id
				sub = "Connecting... ↩ to cancel"
			}
			it := wf.NewItem(co.name).
				Icon(ic).
				Subtitle(sub).
				Arg(action).
				Valid(true)
			if co.status == "Connected" {
				it.NewModifier("cmd").Subtitle(submod)
			}

		}
		if len(conns) == 0 {
			wf.NewItem(`No connections found ¯\_(ツ)_/¯`).
				Icon(aw.IconWarning)
		}
	}
	if *c != "" {
		connect(&gt, *c)
	}
	if *d != "" {
		disconnect(&gt, *d)
	}
	wf.SendFeedback()
}

func main() {
	wf = aw.New()
	wf.Run(run)
}
