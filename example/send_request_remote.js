const fs = require('fs');
const https = require('http');

const bold = fs.readFileSync('./Spectral-Bold.ttf');
const regular = fs.readFileSync('./Spectral-Regular.ttf');
const extraLightItalic = fs.readFileSync('./Spectral-ExtraLightItalic.ttf');

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
				name: 'specimen',
				price: 0,
			},
			{
				name: 'otf',
				price: 15,
			},
		],
		currency: '$',
	},
	paymentNumber: 'ch_1CAfMpEHNnZkutNMqTBlKHOv',
	customerId: 'cus_CZp0g2lQerSnPH',
});

const options = {
	hostname: 'unique-back.prototypo.io',
	port: 443,
	path: '/create-package/',
	method: 'POST',
};

const destFile = fs.createWriteStream('package_remote.zip');
const req = https.request(options, (res) => {
	res.on('data', (chunk) => {
		destFile.write(chunk);
	});
	res.on('end', () => {
		destFile.end();
	});
});

req.write(requestPayload);
req.end();
