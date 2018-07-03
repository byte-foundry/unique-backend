def get_html_email():
	return '''<style type="text/css">
  @media only screen and (max-width: 480px) {
    table {
      display: block !important;
      width: 100% !important;
    }

    td {
      width: 480px !important;
    }
  }
</style>

<body style="font-family: Verdana, sans-serif; margin: 0; padding: 0; width: 100%; background: #FaFaFa; -webkit-text-size-adjust: none; -webkit-font-smoothing: antialiased;">
  <table border="0" cellspacing="0" cellpadding="0" id="background" style="height: 100% !important; margin: 0 auto; padding: 0; width: 600px !important;">
    <tr>
      <td align="center" valign="top">
        <table width="600" border="0" bgcolor="#ffffff" cellspacing="0" cellpadding="0" id="preheader">
          <tr bgcolor="#FFFFFF">
            <td valign="top">
              <table width="100%" border="0" cellspacing="0" cellpadding="0">
                <td valign="top" width="600">
                  <div class="logo">
                    <img style="width: 600px; height: auto;" src="https://i.imgur.com/cVjV9Nf.png" alt="Unique logo" />
                  </div>
                </td>
          </tr>
          </table>
          </td>
    </tr>
    <!-- // END #preheader -->

    <tr bgcolor="#FFFFFF">
      <td align="center" valign="top" class="body_info_content">
        <table width="100%" border="0" cellspacing="0" cellpadding="20">
          <tr>
            <td valign="top">
              <h2 style="color: #000; font-size: 26px; font-weight: bold;">Hi!</h2>
              <p style="color: #a9acaf; font-size: 16px; line-height: 28px; text-align: left;">Yay, you made it, you’ve created a brand new font ready to use in all your projects! We’re so proud of you. <br/> For your reference, we’ve attached your fonts in this email. You should receive the invoice in another email soon.
              </p>
              <p style="color: #a9acaf; font-size: 16px; line-height: 28px; text-align: left;">In case you’ll be back to create an account or visit your Unique font library, we will store your font and look after it for you.
              </p>
              <p style="color: #a9acaf; font-size: 16px; line-height: 28px; text-align: left;">Feel free to spread the word and tell your friends about us! :)
              </p>
              <p style="color: #5320ee; font-size: 16px; line-height: 28px; text-align: left;">Eager to make your next font? <a href="https://unique.prototypo.io/?ref=purchasemail" onmouseover="this.style.color='#622bdd'" onmouseout="this.style.color='#5320ee'" style="color: #5320ee; font-size: 16px; text-decoration: underline;">Let’s go! </a>
              </p> <br/><br/><br/>
              <h2 style="color: #000; font-size: 18px; font-weight: bold;">Best regards, <br/> The Unique team</h2>
            </td>
          </tr>
        </table>
      </td>
    </tr>

    <tr bgColor="#000000" cellspacing="0" cellpadding="20">
      <td align="center" valign="top">
        <table width="100%" border="0" cellspacing="0" cellpadding="20" id="footer">
          <tr>
            <td align="left" valign="top" class="social_container">
              <div class="social">
                <a style="display:inline-block; height:35px; margin:0 0.215em; width:35px;" href="https://www.facebook.com/fontsbyunique/"><img style="width: 25px; height: auto;" src="https://i.imgur.com/OheYzmb.png" alt="Facebook logo"/></a>
                <a style="display:inline-block; height:35px; margin:0 0.215em; width:35px;" href="https://www.instagram.com/fontsbyunique/"><img style="width: 25px; height: auto;" src="https://i.imgur.com/d0H5tmp.png" alt="Instagram logo"/></a>
                <a style="display:inline-block; height:35px; margin:0 0.215em; width:35px;" href="https://twitter.com/fontsbyUnique"><img style="width: 25px; height: auto;" src="https://i.imgur.com/S8n9Mop.png" alt="Twitter logo"/></a>

              </div>
            </td>
            <td align="right" valign="top">
              <p style="color: #aaa; font-size: 12px;">2018  Unique © Powered by Prototypo</p>
            </td>
          </tr>

        </table>
        <!-- // END #footer -->
      </td>
    </tr>
    <!-- // END #footer_container -->
    </td>
    </tr>
    </table>
    <!-- // END #background -->
</body>'''
