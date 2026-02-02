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

</div>

## Windows download

- release: https://shortssh.deus-soft.org/shortssh.exe
- dev: https://shortssh.deus-soft.org/dev-shortssh.exe

### Use installer

`download bat`
```bash
Invoke-WebRequest `
"https://raw.githubusercontent.com/CrudelisDeus/ShortSSH/main/install.bat" `
-OutFile "$env:USERPROFILE\Downloads\ShortSSH-install.bat"
```
`install`
```bash
cd $env:USERPROFILE\Downloads
.\ShortSSH-install.bat
```
