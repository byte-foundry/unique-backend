const fs = require('fs');
const http = require('http');

const bold = fs.readFileSync('./Spectral-Bold.ttf');
const regular = fs.readFileSync('./Spectral-Regular.ttf');
const extraLightItalic = fs.readFileSync('./Spectral-ExtraLightItalic.ttf');

const requestPayload = JSON.stringify({
	family: 'Spectral',
	fonts: [
		{
			variant: 'bold',
			data: bold.toJSON().data,
		},
		{
			variant: 'regular',
			data: regular.toJSON().data,
		},
		{
			variant: 'extra light italic',
			data: extraLightItalic.toJSON().data,
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

console.log(requestPayload);

const options = {
	hostname: 'localhost',
	port: 8003,
	path: '/create-package/',
	method: 'POST',
	headers: {
		origin: 'http://localhost:3000',
	},
};

const destFile = fs.createWriteStream('package.zip');
const req = http.request(options, (res) => {
	res.on('data', (chunk) => {
		destFile.write(chunk);
	});
	res.on('end', () => {
		destFile.end();
	});
});

req.write(requestPayload);
req.end();
