const fs = require('fs');
const http = require('http');

const bold = fs.readFileSync('./Spectral-Bold.ttf');
const regular = fs.readFileSync('./Spectral-Regular.ttf');
const extraLightItalic = fs.readFileSync('./Spectral-ExtraLightItalic.ttf');
const {StringDecoder} = require('string_decoder');

const requestPayload = JSON.stringify({
	family: 'Spectral',
	fonts: [
		{
			variant: 'bold',
			data: bold,
		},
		{
			variant: 'regular',
			data: regular,
		},
		{
			variant: 'extra light italic',
			data: extraLightItalic,
		},
	],
	invoice: {
		choices: [
			{
				name: 'otf',
				price: 15,
			},
		],
		currency: '$',
	},
	paymentNumber: 'ch_1CAfelEHNnZkutNMypcuxw0P',
	customerId: 'cus_CZp0g2lQerSnPH',
});

const options = {
	hostname: 'localhost',
	port: 8000,
	path: '/create-package/',
	method: 'POST',
};

const destFile = fs.createWriteStream('package_no_pdf.zip');
const req = http.request(options, (res) => {
	res.on('data', (chunk) => {
		const decoder = new StringDecoder('utf8');

		console.log(decoder.write(chunk));
	});
	res.on('end', () => {
	});
});

req.write(requestPayload);
req.end();
