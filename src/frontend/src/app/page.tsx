'use client';

import {
    Box, Heading, Text, FormControl, FormLabel, Select, Button, VStack, Input, useToast
} from "@chakra-ui/react";
import React, { useState } from "react";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import { useRouter } from 'next/navigation';

export default function HomePage() {
    const router = useRouter();
    const toast = useToast();
    const [startDate, setStartDate] = useState<Date | null>(null);
    const [endDate, setEndDate] = useState<Date | null>(null);

    const handleSubmit = (event: React.FormEvent) => {
        event.preventDefault();
        router.push('/results');
        toast({
            title: "Planning your trip now...",
            status: "success",
            duration: 3000,
            isClosable: true
        });
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
                        <FormControl id="city">
                            <FormLabel fontWeight="bold" color="gray.600">
                                Select City
                            </FormLabel>
                            <Select placeholder="Choose a city" borderColor="orange.400">
                                <option value="london">London</option>
                                <option value="manchester">Manchester</option>
                                <option value="birmingham">Birmingham</option>
                                <option value="edinburgh">Edinburgh</option>
                            </Select>
                        </FormControl>
                        <FormControl id="trip-type">
                            <FormLabel fontWeight="bold" color="gray.600">
                                Type of Trip
                            </FormLabel>
                            <Select placeholder="Select trip type" borderColor="orange.400">
                                <option value="adventure">Adventure</option>
                                <option value="beach">Beach</option>
                                <option value="city">City</option>
                                <option value="cultural">Cultural</option>
                            </Select>
                        </FormControl>
                        <FormControl id="date">
                            <FormLabel fontWeight="bold" color="gray.600">
                                Select Travel Dates
                            </FormLabel>
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
