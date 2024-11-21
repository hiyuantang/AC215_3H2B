'use client';

import {
    Box, Heading, Text, FormControl, FormLabel, Input, Button, VStack, useToast
} from "@chakra-ui/react";
import React, { useState } from "react";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import { useRouter } from 'next/navigation';

export default function HomePage() {
    const router = useRouter();
    const toast = useToast();
    const [city, setCity] = useState('');
    const [tripType, setTripType] = useState('');
    const [startDate, setStartDate] = useState<Date | null>(null);
    const [endDate, setEndDate] = useState<Date | null>(null);

    const handleSubmit = (event: React.FormEvent) => {
        event.preventDefault();

        if (!city || !tripType || !startDate || !endDate) {
            toast({
                title: "Missing input fields!",
                description: "Please fill in all the required fields.",
                status: "error",
                duration: 3000,
                isClosable: true
            });
            return;
        }

        const days = Math.max(1, Math.ceil((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24)));
        const month = startDate.toLocaleString('default', { month: 'long' });

        router.push(`/results?city=${encodeURIComponent(city)}&days=${days}&type=${encodeURIComponent(tripType)}&month=${encodeURIComponent(month)}`);
    };

    return (
        <Box className="min-h-screen" display="flex" justifyContent="center" alignItems="center" bgGradient="linear(to-r, orange.400, red.400)" p="10">
            <Box bg="white" shadow="2xl" rounded="xl" p="10" width={["full", "md", "lg"]} textAlign="center" color="gray.700">
                <Heading as="h1" size="2xl" fontWeight="extrabold" mb={4} bgGradient="linear(to-r, orange.500, red.500)" bgClip="text">
                    Intelligent Travel Companion
                </Heading>
                <Text fontSize="lg" color="gray.500" mb={8}>
                    Plan your dream trip easily with our AI powered trip advisor
                </Text>
                <form onSubmit={handleSubmit}>
                    <VStack spacing={6} align="stretch">
                        <FormControl id="city" isRequired>
                            <FormLabel fontWeight="bold" color="gray.600">City</FormLabel>
                            <Input
                                placeholder="Enter city"
                                borderColor="orange.400"
                                onChange={(e) => setCity(e.target.value)}
                            />
                        </FormControl>
                        <FormControl id="trip-type" isRequired>
                            <FormLabel fontWeight="bold" color="gray.600">Type of Trip</FormLabel>
                            <Input
                                placeholder="Enter trip type"
                                borderColor="orange.400"
                                onChange={(e) => setTripType(e.target.value)}
                            />
                        </FormControl>
                        <FormControl id="date" isRequired>
                            <FormLabel fontWeight="bold" color="gray.600">Select Travel Dates</FormLabel>
                            <Box display="flex" justifyContent="space-between">
                                <Box flex="1" mr="4">
                                    <DatePicker selected={startDate} onChange={date => setStartDate(date)} customInput={<Input borderColor="orange.400" />} placeholderText="Start date" />
                                </Box>
                                <Box flex="1">
                                    <DatePicker selected={endDate} onChange={date => setEndDate(date)} customInput={<Input borderColor="orange.400" />} placeholderText="End date" />
                                </Box>
                            </Box>
                        </FormControl>
                        <Button type="submit" bgGradient="linear(to-r, orange.400, red.400)" color="white" size="lg" _hover={{ bgGradient: "linear(to-r, orange.500, red.500)" }} py={6} w="full">
                            Plan My Trip
                        </Button>
                    </VStack>
                </form>
            </Box>
        </Box>
    );
}
