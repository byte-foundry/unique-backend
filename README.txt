Installing your font(s) on a computer

This archive contains OpenType fonts, to be installed on your computer (Windows and Mac OSX).


Installation on Windows


Download the provided .zip file
Unzip the .zip file (For example, 7zip that can be downloaded for free at www.7-zip.org)
Open the package folder where .otf file(s) are displayed

then OPTION A :

Double click on each one of the .otf files
Click on Install for each file that you wish to install
Close the window
Restart the computer (recommended)

or OPTION B :

Click on the button Start
Then, open the Control panel
Open the folder with all the .otf files
Copy and paste the .otf files
Restart the computer (recommended)

Installation on Mac OSX


Download the provided .zip file
Unzip the .zip file (For example, 7zip that can be downloaded for free at www.7-zip.org)
Open the package folder where .otf file(s) are displayed

then OPTION A :

Double click on each one of the .otf files
Click on Install for each file that you wish to install
Restart the computer (recommended)

or OPTION B :

Go to your personal account that is usually called “YourName”
Then, click on library (if this folder is not visible by default, you can access it by clicking on +alt in the main menu)
Open the package folder with all the .otf files
Copy and paste the .otf files


Using your font(s) on a website

On your website CSS file, copy the following code, replacing "yourfont" by your font name

@font-face {
  font-family: MyFont;
  src: url({My file url}/myfont.otf)
      format('opentype');
  font-weight: 400;
  font-style: normal;
}
@font-face {
  font-family: MyFont;
  src: url({My file url}/bold.otf)
      format('opentype');
  font-weight: 700;
  font-style: normal;
}

Then integrate the typeface into your CSS.

font-family: 'MyFont', sans-serif;
