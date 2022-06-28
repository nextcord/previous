Need your bot to run 24/7? There's a few ways you can do this:

**1. Get a cheap VPS**
A VPS is a good way to run your bot 24/7, and they can be rented quite cheaply from various companies, some hosts include:
<https://scaleway.com/> (EU)              <https://digitalocean.com/> (US)
<https://linode.com/> (US/EU/Asia)  <https://www.hetzner.com/cloud> (US/EU)
We recommend you compare the options before choosing a provider, and look for other providers that suit you well. It is also possible to use **free trials of services AWS, GCP, and Azure** to run your bot for up to a year for free on a low power machine.

**2. Host locally**
If you have a RaspberryPi this can be used as a bot host quite easily, and many tutorials exist for it online. You can also host a bot on your PC if you keep it on 24/7.
This is not recommended due to the investment involved as well as your network stability
If you are using your PC you should consider using a VPS provider instead.

**3. Free hosting**
Free hosting is not recommended as it is not as stable as a VPS and there will be limitations and potentially rate limits.
If you must choose a free hosting provider, Heroku is the most viable option. By adding a credit card to your Heroku account, you can host a bot 24/7 for free. Make sure to use a `worker` script as `web` scripts will sleep after inactivity.
Use of Replit and EpikHost is discouraged. Replit is designed for websites, which is why they expose a domain for you. EpikHost is known to give away customer information and it is advised that you do not use them for this reason.
