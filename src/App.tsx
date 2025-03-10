import { motion } from 'framer-motion';
import {
	BookOpen,
	Users,
	Trophy,
	Calendar,
	GraduationCap,
	Building2,
	Phone,
	Mail,
	School,
	BookCheck,
	Wrench,
} from 'lucide-react';
import { ImageCarousel } from './components/carousel';
import { carouselImages } from './constants/carousel';

function App() {
	const scrollToFormations = () => {
		document
			.getElementById('formations')
			?.scrollIntoView({ behavior: 'smooth' });
	};

	const containerVariants = {
		hidden: { opacity: 0 },
		visible: {
			opacity: 1,
			transition: {
				staggerChildren: 0.3,
			},
		},
	};

	const itemVariants = {
		hidden: { opacity: 0, y: 20 },
		visible: {
			opacity: 1,
			y: 0,
			transition: {
				duration: 0.5,
			},
		},
	};

	return (
		<div className='min-h-screen bg-white'>
			{/* Hero Section with Carousel */}
			<ImageCarousel images={carouselImages} onLearnMore={scrollToFormations} />

			{/* Historique Section */}
			<motion.div
				initial='hidden'
				whileInView='visible'
				viewport={{ once: true }}
				variants={containerVariants}
				className='py-16 bg-gray-50'
			>
				<div className='container mx-auto px-6'>
					<motion.h2
						variants={itemVariants}
						className='text-4xl font-bold text-center mb-12'
					>
						Notre Histoire
					</motion.h2>
					<div className='max-w-4xl mx-auto text-gray-600 space-y-6 text-lg'>
						<motion.p variants={itemVariants} className='leading-relaxed'>
							Le Lycée Privé Technique Industriel et Commercial de
							Bobo-Dioulasso (LPTIC-B) est un Lycée privé laïc. Il a ouvert ses
							portes pour compter de l'année scolaire 2012-2013 par Autorisation
							N° 2013-001290/MESS/SG/DGESTP du 12 juin 2013 dans les filières du
							génie électrique, de la comptabilité et du secrétariat.
						</motion.p>
						<motion.p variants={itemVariants} className='leading-relaxed'>
							En 2021 par autorisation N° 2021-02436/MENAPLN/SG/DEP du 18
							octobre 2021, il est autorisé à ouvrir les filières du génie
							civil, du génie mécanique et de l'agroalimentaire.
						</motion.p>
					</div>
				</div>
			</motion.div>

			{/* Formations Section */}
			<motion.div
				initial='hidden'
				whileInView='visible'
				viewport={{ once: true }}
				variants={containerVariants}
				id='formations'
				className='py-16 bg-white'
			>
				<div className='container mx-auto px-6'>
					<motion.h2
						variants={itemVariants}
						className='text-3xl font-bold text-center mb-12'
					>
						Nos Formations
					</motion.h2>

					<div className='grid grid-cols-1 md:grid-cols-3 gap-8 mb-12'>
						<motion.div
							variants={itemVariants}
							whileHover={{ scale: 1.05 }}
							className='bg-white p-6 rounded-lg shadow-lg'
						>
							<School className='w-12 h-12 text-blue-600 mb-4' />
							<h3 className='text-xl font-semibold mb-3'>Cycle Court</h3>
							<p className='text-gray-600 mb-4'>3 à 4 ans après le CEP</p>
							<div className='bg-blue-50 p-4 rounded'>
								<p className='font-semibold text-blue-800'>Diplôme: CAP</p>
								<p className='text-sm text-blue-600'>
									Certificat d'Aptitude Professionnelle
								</p>
							</div>
						</motion.div>

						<motion.div
							variants={itemVariants}
							whileHover={{ scale: 1.05 }}
							className='bg-white p-6 rounded-lg shadow-lg'
						>
							<BookCheck className='w-12 h-12 text-blue-600 mb-4' />
							<h3 className='text-xl font-semibold mb-3'>Cycle Moyen</h3>
							<p className='text-gray-600 mb-4'>2 ans après le CAP ou BEPC</p>
							<div className='bg-blue-50 p-4 rounded'>
								<p className='font-semibold text-blue-800'>Diplôme: BEP</p>
								<p className='text-sm text-blue-600'>
									Brevet d'Etude Professionnelle
								</p>
							</div>
						</motion.div>

						<motion.div
							variants={itemVariants}
							whileHover={{ scale: 1.05 }}
							className='bg-white p-6 rounded-lg shadow-lg'
						>
							<GraduationCap className='w-12 h-12 text-blue-600 mb-4' />
							<h3 className='text-xl font-semibold mb-3'>Cycle Long</h3>
							<p className='text-gray-600 mb-4'>2 ans après le BEP</p>
							<div className='bg-blue-50 p-4 rounded'>
								<p className='font-semibold text-blue-800'>Diplôme: BAC Pro</p>
								<p className='text-sm text-blue-600'>
									Baccalauréat Professionnel
								</p>
							</div>
						</motion.div>
					</div>

					<motion.div
						variants={itemVariants}
						className='bg-white p-6 rounded-lg shadow-lg text-center'
					>
						<p className='text-gray-600'>
							L'enseignement technologique est un cycle long qui conduit au
							Baccalauréat technologique des séries G et F. <br /> On y accède à
							travers une seconde AB3 ou une seconde TI après l'obtention du
							BEPC.
						</p>
					</motion.div>
				</div>
			</motion.div>

			{/* Filières Section */}
			<motion.div
				initial='hidden'
				whileInView='visible'
				viewport={{ once: true }}
				variants={containerVariants}
				className='py-16 bg-gray-50'
				id='filieres'
			>
				<div className='container mx-auto px-6'>
					<motion.h2
						variants={itemVariants}
						className='text-3xl font-bold text-center mb-12'
					>
						Nos Filières
					</motion.h2>
					<div className='grid grid-cols-1 md:grid-cols-3 gap-6'>
						{[
							{
								icon: Wrench,
								title: 'Génie Électrique',
								desc: 'Électronique et Électrotechnique',
							},
							{
								icon: BookOpen,
								title: 'Administration',
								desc: 'Comptabilité et Secrétariat',
							},
							{
								icon: Trophy,
								title: 'Génie Civil',
								desc: 'Construction et Travaux Publics',
							},
							{
								icon: Users,
								title: 'Génie Mécanique',
								desc: 'Maintenance Industrielle',
							},
							{
								icon: Calendar,
								title: 'Agroalimentaire',
								desc: 'Transformation et Production',
							},
						].map((filiere, index) => (
							<motion.div
								key={index}
								variants={itemVariants}
								whileHover={{ scale: 1.05 }}
								className='p-6 bg-white rounded-lg shadow-lg'
							>
								<filiere.icon className='w-12 h-12 text-blue-600 mb-4' />
								<h3 className='text-xl font-semibold mb-3'>{filiere.title}</h3>
								<p className='text-gray-600'>{filiere.desc}</p>
							</motion.div>
						))}
					</div>
				</div>
			</motion.div>

			{/* Contact Section */}
			<motion.div
				initial='hidden'
				whileInView='visible'
				viewport={{ once: true }}
				variants={containerVariants}
				className='py-16 bg-white'
				id='contact'
			>
				<div className='container mx-auto px-6'>
					<motion.div
						variants={itemVariants}
						className='bg-blue-600 rounded-lg shadow-xl text-white p-8'
					>
						<div className='grid grid-cols-1 md:grid-cols-2 gap-8'>
							<div>
								<h2 className='text-3xl font-bold mb-6'>Contactez-nous</h2>
								<div className='flex items-center mb-4'>
									<Building2 className='mr-3' />
									<p>01 B.P 3697 Bobo-Dioulasso</p>
								</div>
								<div className='flex items-center mb-4'>
									<Phone className='mr-3' />
									<p>20 97 25 35 / 76 61 17 46 / 70 39 46 16</p>
								</div>
								<div className='flex items-center'>
									<Mail className='mr-3' />
									<p>ssibiri2@yahoo.fr</p>
								</div>
							</div>
							<div>
								<h3 className='text-xl font-semibold mb-4'>
									Planifiez une visite
								</h3>
								<p className='mb-6'>
									Découvrez notre campus et rencontrez nos enseignants pour en
									savoir plus sur nos formations.
								</p>
								<motion.button
									whileHover={{ scale: 1.05 }}
									whileTap={{ scale: 0.95 }}
									className='bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100'
								>
									<a href='mailto:ssibiri2@yahoo.fr'>Réserver une visite</a>
								</motion.button>
							</div>
						</div>
					</motion.div>
				</div>
			</motion.div>

			{/* Footer */}
			<footer className='bg-gray-900 text-white py-8'>
				<div className='container mx-auto px-6'>
					<div className='flex items-center justify-between'>
						<motion.div
							initial={{ opacity: 0, x: -20 }}
							animate={{ opacity: 1, x: 0 }}
							className='flex items-center'
						>
							<GraduationCap className='w-8 h-8 mr-2' />
							<span className='text-xl font-bold'>LPTIC-B</span>
						</motion.div>
						<motion.div
							initial={{ opacity: 0, x: 20 }}
							animate={{ opacity: 1, x: 0 }}
							className='flex space-x-6'
						>
							<a href='/' className='hover:text-blue-400'>
								Accueil
							</a>
							<a href='#formations' className='hover:text-blue-400'>
								Formations
							</a>
							<a href='#filieres' className='hover:text-blue-400'>
								Filières
							</a>
							<a href='#contact' className='hover:text-blue-400'>
								Contact
							</a>
						</motion.div>
					</div>
					<motion.div
						initial={{ opacity: 0, y: 20 }}
						animate={{ opacity: 1, y: 0 }}
						transition={{ delay: 0.2 }}
						className='mt-6 text-center text-gray-400'
					>
						<p>
							&copy; {new Date().getFullYear()} LPTIC-B. Tous droits réservés.
						</p>
					</motion.div>
				</div>
			</footer>
		</div>
	);
}

export default App;
