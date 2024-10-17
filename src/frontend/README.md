## Getting Started
To run locally, make sure you have Node.js installed on your machine. You can download it from [here](https://nodejs.org/en/download/). Then, install the dependencies and configure the Google Maps API Key. This API Key is required to run the application as intended. You can get a Google Maps API key from [here](https://developers.google.com/maps/documentation/javascript/get-api-key).

### Environment Variables
Create a `.env.local` file in the root of the project and add the following environment variables:
```bash
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=<API_KEY_HERE>
```

### Running Locally
```bash
npm install
npm run dev
```

## Running with Docker
```bash
docker build --build-arg NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=<API_KEY_HERE> -t trip-advisor-ui . # Builds with the Google Maps API key
docker run -p 3000:3000 trip-advisor-ui
```
