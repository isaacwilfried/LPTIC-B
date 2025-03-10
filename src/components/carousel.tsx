import { useState, useEffect } from 'react';
import {
	ChevronLeft,
	ChevronRight,
	ChevronRight as ChevronRightIcon,
} from 'lucide-react';

interface ImageCarouselProps {
	images: {
		src: string;
		alt: string;
		caption?: string;
	}[];
	autoPlayInterval?: number;
	onLearnMore?: () => void;
}

export function ImageCarousel({
	images,
	autoPlayInterval = 5000,
	onLearnMore,
}: ImageCarouselProps) {
	const [currentIndex, setCurrentIndex] = useState(0);

	useEffect(() => {
		const timer = setInterval(() => {
			setCurrentIndex(current => (current + 1) % images.length);
		}, autoPlayInterval);

		return () => clearInterval(timer);
	}, [images.length, autoPlayInterval]);

	const goToNext = () => {
		setCurrentIndex(current => (current + 1) % images.length);
	};

	const goToPrevious = () => {
		setCurrentIndex(current => (current - 1 + images.length) % images.length);
	};

	const goToSlide = (index: number) => {
		setCurrentIndex(index);
	};

	return (
		<div className='relative w-full h-[600px] overflow-hidden group'>
			{/* Images */}
			<div
				className='absolute w-full h-full transition-transform duration-500 ease-in-out'
				style={{ transform: `translateX(-${currentIndex * 100}%)` }}
			>
				{images.map((image, index) => (
					<div
						key={index}
						className='absolute top-0 left-0 w-full h-full'
						style={{ transform: `translateX(${index * 100}%)` }}
					>
						<img
							src={image.src}
							alt={image.alt}
							className='w-full h-full object-cover'
						/>
						{image.caption && (
							<div className='absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 text-white p-4'>
								<p className='text-lg'>{image.caption}</p>
							</div>
						)}
					</div>
				))}
			</div>

			{/* Hero Content Overlay */}
			<div className='absolute inset-0 bg-black/50'>
				<div className='container mx-auto px-6 h-full flex items-center'>
					<div className='max-w-3xl text-white'>
						<h1 className='text-5xl font-bold mb-6'>
							Lycée Privé Technique Industriel et Commercial de Bobo-Dioulasso
							(LPTIC-B)
						</h1>
						<p className='text-xl mb-8'>
							Formation d'excellence en génie électrique, comptabilité,
							secrétariat, génie civil, génie mécanique et agroalimentaire.
						</p>
						<button
							onClick={onLearnMore}
							className='bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-semibold flex items-center'
						>
							En savoir plus <ChevronRightIcon className='ml-2' size={20} />
						</button>
					</div>
				</div>
			</div>

			{/* Navigation Buttons */}
			<button
				onClick={goToPrevious}
				className='absolute left-4 top-1/2 -translate-y-1/2 bg-black/30 hover:bg-black/50 text-white p-2 rounded-full opacity-0 group-hover:opacity-100 transition-opacity'
			>
				<ChevronLeft size={24} />
			</button>
			<button
				onClick={goToNext}
				className='absolute right-4 top-1/2 -translate-y-1/2 bg-black/30 hover:bg-black/50 text-white p-2 rounded-full opacity-0 group-hover:opacity-100 transition-opacity'
			>
				<ChevronRight size={24} />
			</button>

			{/* Indicators */}
			<div className='absolute bottom-4 left-1/2 -translate-x-1/2 flex space-x-2'>
				{images.map((_, index) => (
					<button
						key={index}
						onClick={() => goToSlide(index)}
						className={`w-2 h-2 rounded-full transition-all ${
							index === currentIndex ? 'bg-white w-4' : 'bg-white/50'
						}`}
					/>
				))}
			</div>
		</div>
	);
}
