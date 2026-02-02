<div align="center">
  <h1>ShortSSH</h1>

  <img src="./readme/img/logo1.gif" alt="logo">

  <p>ShortSSH is your personal SSH manager in the terminal. It simplifies working with SSH hosts, keys, and configuration, removing the hassle and mistakes of manual setup.</p>
  <!-- <img src="./readme/img/welcome.gif"> -->


<h2>Example usage</h2>

<table>
    <thead>
        <tr>
            <th>Example</th>
            <th>Standart command</th>
            <th>ShortSSH</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>1 ssh connect</td>
            <td>ssh dmytro@192.168.1.112</td>
            <td>ssh 1112</td>
        </tr>
        <tr>
            <td>2 rsync</td>
            <td>rsync rvu ./* dmytro@192.168.1.112:/home</td>
            <td>rsync rvu ./* 1112:/home</td>
        </tr>
    </tbody>
</table>

<h2>Windows download</h2>

<table>
    <thead>
        <tr>
            <th>Name</th>
            <th>Link</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Release link</td>
            <td>https://shortssh.deus-soft.org/shortssh.exe</td>
        </tr>
        <tr>
            <td>Release link</td>
            <td>https://shortssh.deus-soft.org/dev-shortssh.exe</td>
        </tr>
    </tbody>
</table>

<h3>Manual</h3>

</div>

`powershell`
```bash
Invoke-WebRequest `
"https://raw.githubusercontent.com/CrudelisDeus/ShortSSH/main/install.bat" `
-OutFile "$env:USERPROFILE\Downloads\ShortSSH-install.bat"
```

```bash
cd $env:USERPROFILE\Downloads
.\ShortSSH-install.bat
```
