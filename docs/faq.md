#Common Questions and Answers

## Can I sign in with Google?

Yes you can! Pass the flag `-a google` (replacing `-a ptc`) to use Google authentication. 

If you happen to have 2-step verification enabled for your Google account you will need to supply an [app password](https://support.google.com/accounts/answer/185833?hl=en) for your password instead of your normal login password.


## ...expected one argument.

The -dp, -dg -dl, -i, -o and -ar parameters are no longer needed. Remove them from your query.

## How do I setup port forwarding?

[See this helpful guide](external.md)

## "It's acting like the location flag is missing.

`-l`, never forget.

## I'm getting this error...

| Error  |  Cause |
|---|---|
| `pip or python is not recognized as an internal or external command`  | [Python/pip has not been added to the environment](https://github.com/Langoor2/PokemonGo-Map-FAQ/blob/master/FAQ/Enviroment_Variables_not_correct.md)  |
| `pip or python is not recognized as an internal or external command`  | [pip needs to be installed to retrieve all the dependencies](https://github.com/AHAAAAAAA/PokemonGo-Map/wiki/Installation-and-requirements)  |
| `Exception, e <- Invalid syntax.`  | This error is caused by Python 3. The project requires python 2.7  |
| `error: command 'gcc' failed with exit status 1`  | Your OS is missing the `gcc` compiler library. <ul><li>For Debian, run `apt-get install build-essentials`</li> <li>For Red Hat, run `yum groupinstall 'Development Tools'`</li></ul> |
| `[...]failed with error code 1 in /tmp/pip-build-k3oWzv/pycryptodomex/`   | Your OS is missing the `gcc` compiler library. <ul><li>For Debian, run `apt-get install build-essentials`</li> <li>For Red Hat, run `yum groupinstall 'Development Tools'`</li></ul>